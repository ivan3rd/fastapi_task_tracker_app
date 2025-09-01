import uuid

import pytest
from sqlalchemy import select, delete, func

from app.models import TaskModel
from app.types import TaskStatusTypeEnum


@pytest.mark.asyncio(loop_scope="session")
async def test_tasks(db_session, auth_client):
    task_data = {'name': 'test task', 'description': 'create_task'}

    response = await auth_client.post('/tasks', json=task_data)
    assert response.status_code == 201

    r_data = response.json()
    assert 'name' in r_data
    assert r_data['name'] == task_data['name']
    assert 'description' in r_data
    assert r_data['description'] == task_data['description']

    assert 'id' in r_data
    assert r_data['id'] is not None
    assert 'status' in r_data
    assert r_data['status'] == TaskStatusTypeEnum.CREATED

    response = await auth_client.get(f"/tasks/{uuid.uuid4()}")
    assert response.status_code == 404

    response = await auth_client.get(f"/tasks/{r_data['id']}")
    assert response.status_code == 200

    n_data = response.json()
    assert n_data['id'] == r_data['id']
    assert n_data['name'] == r_data['name']
    assert n_data['description'] == r_data['description']

    # put
    edit_data = {
        'name': 'New name',
        'description': 'some other description',
        'status': TaskStatusTypeEnum.IN_PROGRESS,
    }
    response = await auth_client.put(f"/tasks/{uuid.uuid4()}", json=edit_data)
    assert response.status_code == 404

    response = await auth_client.put(f"/tasks/{r_data['id']}")
    assert response.status_code == 422

    response = await auth_client.put(f"/tasks/{r_data['id']}", json=edit_data)
    assert response.status_code == 200

    n_data = response.json()
    assert n_data['name'] == edit_data['name']
    assert n_data['description'] == edit_data['description']
    assert n_data['status'] == edit_data['status']

    edit_data['status'] = TaskStatusTypeEnum.FINISHED

    response = await auth_client.put(f"/tasks/{r_data['id']}", json=edit_data)
    assert response.status_code == 200

    n_data = response.json()
    assert n_data['name'] == edit_data['name']
    assert n_data['description'] == edit_data['description']
    assert n_data['status'] == edit_data['status']
    assert n_data['created_at'] == r_data['created_at']
    assert n_data['updated_at'] != r_data['updated_at']

    response = await auth_client.get(f"/tasks/{r_data['id']}")
    assert response.status_code == 200
    n_data = response.json()
    assert n_data['name'] == edit_data['name']
    assert n_data['description'] == edit_data['description']
    assert n_data['updated_at'] != r_data['updated_at']

    # delete
    response = await auth_client.delete(f"/tasks/{uuid.uuid4()}")
    assert response.status_code == 404

    response = await auth_client.delete(f"/tasks/{r_data['id']}")
    assert response.status_code == 204

    task = await TaskModel.get_task(r_data['id'])
    assert task is None


@pytest.mark.asyncio(loop_scope="session")
async def test_pagination_tasks(db_session, auth_client):
    tasks = []
    for n in range(0, 10):
        task = TaskModel(
            name=f'Name {n}',
            description=f'Description {n}',
            status=TaskStatusTypeEnum.IN_PROGRESS if n < 5 else TaskStatusTypeEnum.CREATED
        )
        tasks.append(task)
        db_session.add(task)

    await db_session.flush()

    response = await auth_client.get(f"/tasks")
    assert response.status_code == 200

    list_data = response.json()
    assert list_data['current_page'] == 1
    assert list_data['page_size'] == 100
    assert list_data['total_pages'] == 1
    assert list_data['total_items'] == len(tasks)

    for response_task, db_task in zip(list_data['results'], tasks):
        assert response_task['id'] == str(db_task.id)
        assert response_task['name'] == db_task.name
        assert response_task['description'] == db_task.description

    response = await auth_client.get(f"/tasks?page=1&page_size=5")
    assert response.status_code == 200

    list_data = response.json()
    assert list_data['current_page'] == 1
    assert list_data['page_size'] == 5
    assert list_data['total_pages'] == 2
    assert list_data['total_items'] == len(tasks)

    assert len(list_data['results']) == len(tasks[:5])
    for response_task, db_task in zip(list_data['results'], tasks[:5]):
        assert response_task['id'] == str(db_task.id)
        assert response_task['name'] == db_task.name
        assert response_task['description'] == db_task.description


    response = await auth_client.get(f"/tasks?page=2&page_size=5")
    assert response.status_code == 200

    list_data = response.json()
    assert list_data['current_page'] == 2
    assert list_data['page_size'] == 5
    assert list_data['total_pages'] == 2
    assert list_data['total_items'] == len(tasks)

    assert len(list_data['results']) == len(tasks[5:])
    for response_task, db_task in zip(list_data['results'], tasks[5:]):
        assert response_task['id'] == str(db_task.id)
        assert response_task['name'] == db_task.name
        assert response_task['description'] == db_task.description

    response = await auth_client.get(f"/tasks?page=3&page_size=5")
    assert response.status_code == 200

    list_data = response.json()
    assert list_data['current_page'] == 3
    assert list_data['page_size'] == 5
    assert list_data['total_pages'] == 2
    assert list_data['total_items'] == len(tasks)

    assert len(list_data['results']) == 0

    response = await auth_client.get(f"/tasks?task_status={TaskStatusTypeEnum.IN_PROGRESS}")
    assert response.status_code == 200
    list_data = response.json()

    in_progress_tasks = [_ for _ in tasks if _.status == TaskStatusTypeEnum.IN_PROGRESS]
    assert list_data['total_items'] == len(in_progress_tasks)
    # cleaning database from tasks
    await db_session.execute(delete(TaskModel).where(TaskModel.id.in_([_.id for _ in tasks])))
    assert await db_session.scalar(func.count(select(TaskModel.id))) == 0

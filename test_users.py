import requests

BASE_URL = "http://localhost:5000"
REGISTER_URL = f"{BASE_URL}/register"
LOGIN_URL = f"{BASE_URL}/login"
TASKS_URL = f"{BASE_URL}/tasks"

def get_token(username, password):
    response = requests.post(LOGIN_URL, json={"username": username, "password": password})
    if response.status_code == 200:
        print(f"Пользователь {username} успешно авторизован.")
        return response.json().get('access_token')
    else:
        print(f"Ошибка авторизации: {response.status_code}, {response.json()}")
        return None

# Тесты
def test_register_user(username, password):
    response = requests.post(REGISTER_URL, json={"username": username, "password": password})
    if response.status_code == 201:
        print(f"Пользователь {username} успешно зарегистрирован.")
    else:
        print(f"Ошибка регистрации: {response.status_code}, {response.json()}")

def test_create_task(token, title, description=None):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(TASKS_URL, json={"title": title, "description": description, "done": False}, headers=headers)
    if response.status_code == 201:
        print("Задача успешно создана:", response.json())
    else:
        print(f"Ошибка создания задачи: {response.status_code}, {response.json()}")

def test_get_tasks(token):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(TASKS_URL, headers=headers)
    if response.status_code == 200:
        print("Список задач:", response.json())
    else:
        print(f"Ошибка получения задач: {response.status_code}, {response.json()}")

def test_get_task_by_id(token, task_id):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{TASKS_URL}/{task_id}", headers=headers)
    if response.status_code == 200:
        print("Задача успешно получена:", response.json())
    elif response.status_code == 404:
        print("Задача не найдена.")
    else:
        print(f"Ошибка получения задачи: {response.status_code}, {response.json()}")

def test_update_task(token, task_id, title, description, done):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.put(f"{TASKS_URL}/{task_id}", json={
        "title": title,
        "description": description,
        "done": done
    }, headers=headers)
    if response.status_code == 200:
        print("Задача успешно обновлена:", response.json())
    else:
        print(f"Ошибка обновления задачи: {response.status_code}, {response.json()}")

def test_delete_task(token, task_id):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.delete(f"{TASKS_URL}/{task_id}", headers=headers)
    if response.status_code == 204:
        print("Задача успешно удалена.")
    else:
        print(f"Ошибка удаления задачи: {response.status_code}, {response.json()}")

def test_get_users(token):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{BASE_URL}/users", headers=headers)
    if response.status_code == 200:
        print("Список пользователей:", response.json())
    else:
        print(f"Ошибка получения пользователей: {response.status_code}, {response.json()}")

# Запуск тестов
if __name__ == "__main__":

    username = "test_user"
    password = "password123"

    username_2 = "Daniil_Beda"
    password_2 = "12345"

    # Регистрация пользователя
    print("Тест регистрации первого пользователя:")
    test_register_user(username, password)

    # # Авторизация и получение токена
    print("\nТест авторизации пользователя:")
    token = get_token(username, password)
    if not token:
        print("Не удалось выполнить авторизацию. Тесты остановлены.")
        exit()

    #
    # Тесты с задачами
    print("\nТест на создание задач:")
    test_create_task(token, "Первая задача", "Описание первой задачи")
    test_create_task(token, "Вторая задача", "Описание второй задачи")

    print("\nТест на создание задач с пустым Title:")
    test_create_task(token, None, "Описание еще одной задачи")

    print("\nТест получения списка задач:")
    test_get_tasks(token)
    #
    print("\nТест на получение конкретной задачи:")
    test_get_task_by_id(token, task_id=1)

    print("\nТест на получение несуществующей задачи:")
    test_get_task_by_id(token, task_id=3)


    print("\nТест обновления задачи:")
    test_update_task(token, 1, "Обновленная первая задача", "Новое описание первой задачи", True)
    
    print("\nТест обновления несуществующей задачи:")
    test_update_task(token, 3, "Обновленная третья задача", "Новое описание третьей задачи", True)

    print("\nТест получения списка задач после обновления:")
    test_get_tasks(token)

    #
    print("\nТест удаления задачи:")
    test_delete_task(token, 1)

    print("\nТест удаления несуществующей задачи:")
    test_delete_task(token, 10)
    #
    print("\nТест получения списка задач после удаления:")
    test_get_tasks(token)



    # Регистрация второго пользователя
    print("Тест регистрации второго пользователя:")
    test_register_user(username_2, password_2)

    # # Авторизация и получение токена для второго пользователя
    print("\nТест авторизации второго пользователя:")
    token_2 = get_token(username_2, password_2)
    if not token:
        print("Не удалось выполнить авторизацию. Тесты остановлены.")
        exit()

    print("\nТест на создание задач:")
    test_create_task(token_2, "Первая задача по Python", "Описание первой задачи")

    print("\nТест получения списка задач второго пользователя:")
    test_get_tasks(token_2)

    print("\nТест удаления вторым пользователем задачи, которую создал первый:")
    test_delete_task(token_2, 2)

    print("\nТест обновления вторым пользователем задачи, которую создал первый:")

    test_update_task(token_2, 2, "Обновленная вторая задача", "Новое описание второй задачи", True)

    print("\nТест для получения списка пользователей БД")
    test_get_users(token_2)

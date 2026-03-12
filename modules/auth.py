def login_control(username: str, password: str) -> bool:
    demo_users = {
        "firma1": "1234",
        "admin": "admin123",
        "demo": "demo"
    }
    return demo_users.get(username) == password

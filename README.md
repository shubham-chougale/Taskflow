
## Project Structure

```
taskflow-backend/
│
├── app/
│   ├── main.py                      # App bootstrap
│   │
│   ├── core/                        # Global system config
│   │   ├── __init__.py
│   │   ├── config.py                # env, settings
│   │   ├── security.py              # JWT, hashing
│   │   ├── dependencies.py          # get_current_user (manual JWT)
│   │   ├── logging.py               # logging config 
│   │   └── exceptions.py            # global errors 
│   │
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   └── models/
│   │       ├── user.py
│   │       ├── team.py
│   │       └── task.py
│   │
│   ├── repositories/                # DB ONLY 
│   │   ├── __init__.py
│   │   ├── user_repo.py
│   │   ├── team_repo.py
│   │   └── task_repo.py
│   │
│   ├── services/                    # BUSINESS LOGIC 
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── task_service.py
│   │   └── user_service.py
│   │   ├── __init__.py
│   │   ├── auth_controller.py
│   │   └── task_controller.py
│   │
│   ├── api/                         # Routers ONLY
│   │   ├── __init__.py
│   │   ├── auth_routes.py           # thin routes 
│   │   └── task_routes.py           # thin routes 
│   │
│   ├── schemas/                     # DTOs
│   │   ├── auth.py
│   │   ├── user.py
│   │   └── task.py
│   │
│   ├── utils/
│   │   ├── file_storage.py          # uploads, assets 
│   │   ├── helpers.py
│   │   └── genai.py                 # future AI
│   │
│   └── logs/                        # log output 
│       └── app.log
│
├── alembic/
├── requirements.txt
└── README.md
```
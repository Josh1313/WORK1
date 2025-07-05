# Project Structure Diagram

Below is a visual, tree-like representation of the project directory structure with key files and folders annotated to convey their purpose clearly.

```plaintext
root/
├── backend/                        # Backend API server (FastAPI)
│   ├── app/
│   │   ├── api/                   # API endpoints (REST routes)
│   │   │   └── routes/
│   │   │       └── __init__.py    # Route module registration
│   │   │
│   │   ├── schema/
│   │   │   └── files/
│   │   │       └── __init__.py    # Pydantic schemas (data validation)
│   │   │
│   │   ├── services/
│   │   │   └── files/
│   │   │       └── __init__.py   # Business logic & storage management
│   │   │
│   │   ├── utils/
│   │   │   └── files/
│   │   │       └── __init__.py   # Utilities (e.g., logging setup) 
│   │   │
│   │   │
│   │   ├── config.py              # App configuration, env vars, OpenAI API keys
│   │   ├── main.py                # FastAPI instantiation, middleware, lifecycle
│   │                  
│   ├── dockerfile/
│   │       
│   │   
│   │                    
│   │
│   └── data/                     # Persistent & temp data storage
│       ├── datasets/              # User-uploaded datasets (CSV, XLSX)
│       └── temp/                  # Temporary files for processing
│
├── frontend/                      # Frontend (Streamlit)
│   ├── api_client.py             # Python client for backend API communication
│   ├── main.py                   # Streamlit multi-page app with navigation & backend health
│   ├── utils/                    # Frontend helper utilities (styling, etc.)
│   ├── .env                     # Frontend environment variables
│   └── pages/
│   ├── dockerfile.yml                   # Streamlit UI pages (home, files, chat, about)
│   
├── docker-compose.yml            # Service orchestration for backend & frontend containers
├── README.MD                    # System architecture diagram & documentation overview
└── .env                         # Backend environment variables/configuration
```

### Diagram Key Points

- Lines (`├──` and `└──`) indicate folder hierarchy and organization.
- Indentation depth shows nesting level.
- Comments to the right briefly describe file or folder purpose.
- Backend and Frontend are distinct, reflecting separation of concerns.
- `data/` folder inside backend for file persistence.
- `api_client.py` in frontend abstracts HTTP interactions.
- `main.py` files serve as main entry points for backend API and frontend UI respectively.
- Configuration is centralized in `config.py` and `.env` files.

This format should help you quickly grasp the system layout visually and understand component responsibilities.
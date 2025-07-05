
# Database Component Analysis

 In this section, I'll provide a comprehensive analysis of the database component architecture, responsibilities, and implementation details.

## Database Component Overview

The database component implemented as a **file-based storage system** rather than a traditional database server. Here's the detailed analysis:

### Architecture and Location

The database component is primarily located in:
- **`backend/data/`** - Data storage layer
  - `datasets/` - User-uploaded datasets (CSV, XLSX)
  - `temp/` - Temporary files for processing
- **`backend/app/services/`** - Business logic & storage management
- **`backend/app/config.py`** - Database configuration and connection settings

## Database Architecture Diagram

```mermaid
graph TD
    subgraph "Frontend Layer"
        A[Streamlit UI] --> B[API Client]
    end
    
    subgraph "Backend API Layer"
        B --> C[FastAPI Routes]
        C --> D[API Endpoints]
        D --> E[Storage Service]
    end
    
    subgraph "Business Logic Layer"
        E --> F[Data Validation]
        E --> G[File Processing]
        E --> H[Storage Operations]
    end
    
    subgraph "Data Storage Layer"
        H --> I[(SQLite Database)]
        H --> J[File System Storage]
        
        subgraph "Physical Storage"
            J --> K[backend/data/datasets/]
            J --> L[backend/data/temp/]
            I --> M[app.db]
        end
    end
    
    subgraph "Configuration Layer"
        N[config.py] --> E
        N --> I
    end
    
    style I fill:#e1f5fe,color:#000000
    style J fill:#f3e5f5,color:#000000
    style K fill:#e8f5e8
    style L fill:#fff3e0
    style M fill:#e1f5fe
```

## Component Responsibilities

### 1. Storage Service (`backend/app/services/`)
- **Primary Role**: Abstracts database operations and file management
- **Responsibilities**:
  - CRUD operations for datasets
  - File upload/download handling
  - Data persistence management
  - Database connection management

### 2. Data Layer (`backend/data/`)
- **datasets/**: Persistent storage for user-uploaded files
- **temp/**: Temporary processing files and cache
- **app.db**: SQLite database file (inferred from typical FastAPI patterns)

### 3. Configuration (`backend/app/config.py`)
- Database connection strings
- File storage paths
- Upload size limits
- Environment-specific settings

## Implementation Details

### Database Technology Stack
The project structure and common FastAPI patterns:

```mermaid
graph LR
    subgraph "Database Stack"
        A[SQLite] --> B[aiosqlite/SQLAlchemy]
        B --> C[Pydantic Models]
        C --> D[FastAPI Endpoints]
    end
    
    subgraph "File Storage"
        E[Local File System] --> F[Python pathlib]
        F --> G[File Validation]
        G --> H[Storage Service]
    end
    
    style A fill:#81c784
    style E fill:#ffb74d
```

###  Database Schema

```mermaid
erDiagram
    DATASETS {
        int id PK
        string filename
        string original_name
        string file_type
        int file_size
        datetime uploaded_at
        string file_path
        json metadata
    }
    
    CHAT_HISTORY {
        int id PK
        int dataset_id FK
        string message
        string response
        datetime timestamp
        string session_id
    }
    
    PROCESSING_JOBS {
        int id PK
        int dataset_id FK
        string job_type
        string status
        json parameters
        datetime created_at
        datetime completed_at
    }
    
    DATASETS ||--o{ CHAT_HISTORY : "has"
    DATASETS ||--o{ PROCESSING_JOBS : "processes"
```

## Data Flow Architecture

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant API as FastAPI
    participant S as Storage Service
    participant DB as Database
    participant FS as File System
    
    U->>F: Upload Dataset
    F->>API: POST /files/upload
    API->>S: save_dataset()
    S->>FS: Store file in /datasets/
    S->>DB: Insert metadata
    DB-->>S: Confirm insertion
    S-->>API: Return dataset_id
    API-->>F: Success response
    F-->>U: Upload complete
    
    U->>F: Query Dataset
    F->>API: GET /datasets/{id}
    API->>S: get_dataset()
    S->>DB: Query metadata
    S->>FS: Load file if needed
    S-->>API: Return data
    API-->>F: Dataset info
    F-->>U: Display results
```

## Key Design Patterns

### 1. **Repository Pattern**
- Storage Service acts as repository
- Abstracts database operations
- Provides clean interface for data access

### 2. **File System + Database Hybrid**
- Metadata stored in database
- Large files stored in file system
- Efficient for handling datasets

### 3. **Async Operations**
- Non-blocking database operations
- Concurrent file processing
- Better performance for I/O operations

## Configuration Structure

```mermaid
graph TD
    subgraph "Environment Configuration"
        A[.env] --> B[config.py]
        B --> C[Database Settings]
        B --> D[File Storage Settings]
        B --> E[API Settings]
    end
    
    subgraph "Database Configuration"
        C --> F[DATABASE_URL]
        C --> G[CONNECTION_POOL_SIZE]
        C --> H[QUERY_TIMEOUT]
    end
    
    subgraph "Storage Configuration"
        D --> I[UPLOAD_PATH]
        D --> J[MAX_FILE_SIZE]
        D --> K[ALLOWED_EXTENSIONS]
    end
```

## Summary

The database component implements a **hybrid storage architecture** combining:
- **SQLite database** for metadata and structured data
- **File system storage** for large datasets
- **Service layer abstraction** for clean separation of concerns
- **Async operations** for better performance


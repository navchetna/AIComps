# DocFlow - Document Flow Management System

A comprehensive document management system with user authentication, role-based access control, and group-based document permissions.

## 📋 Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [System Architecture](#system-architecture)
- [Initial Setup](#initial-setup)
- [User Management](#user-management)
- [Admin Panel Guide](#admin-panel-guide)
- [API Reference](#api-reference)
- [Docker Deployment](#docker-deployment)
- [Development](#development)

## Overview

DocFlow provides a complete solution for managing document access with:

- **User Authentication** - Session-based login with secure password hashing
- **Role-Based Access Control** - Admin and User roles with different permissions
- **Group Management** - Organize users into groups (Engineering, Marketing, etc.)
- **Document Permissions** - Control which groups can access which documents
- **Admin Panel** - Comprehensive UI for managing users, groups, and permissions
- **Document Viewer** - Browse and view parsed document structures
- **Dark Mode** - Full dark/light theme support


# Quick Start

## Prerequisites

### 1) Node.js Installation
Install the latest version of Node.js from [nodejs.org](https://nodejs.org/en/download)

- Select **Node.js v**. **(LTS)**
- Platform: **Linux**
- Installation method: **nvm**
- Package manager: **npm**

Follow the installation steps provided for your system.

### 2) MongoDB Setup
MongoDB must be running on `localhost:27017`

Start MongoDB using Docker:
```bash
docker run --name doc-flow-mongo -d -p 27017:27017 mongo:latest
```

### 3) Directory Setup
Ensure PDF processing results are available in the `~/pdf-results` directory.

---

## Installation Steps - Development

### Backend Setup
```bash
cd AIComps/input-handlers/pdf/viewer/backend

# Install dependencies
npm install

# Initialize admin user and group
npm run init-admin

# Initialize documents with admin permissions
# Set environment variables for PDF directories
export PDF_RESULTS_DIR=/path/to/pdf-results  # Outputs of the PDF parser
export PDFS_DIR=/path/to/pdfs-dir            # Directory containing PDFs to render
npm run init-docs

# Start backend server
npm run dev
```

### Frontend Setup

Open a new terminal and run:
```bash
cd AIComps/input-handlers/pdf/viewer/frontend

# Install dependencies
npm install

# Configure environment variable
export NEXT_PUBLIC_API_URL=http://localhost:5001

# Start frontend
npm run dev
```

---

## Accessing the Application via Remote Server

To access the application hosted on a remote server through a jump server, use SSH tunneling.
> Note: This would apply even with the Docker setup
### SSH Tunneling Format
```bash
ssh -L <frontend_client_port>:localhost:<frontend_server_port> \
    -L <backend_client_port>:localhost:<backend_server_port> \
    -J <jumperserver_username>@<jump_ip>:<jump_port> \
    <remoteserver_username>@<remoteserver_ip>
```

### Example Command
```bash
ssh -L 3000:localhost:3000 \
    -L 5001:localhost:5001 \
    -J ritik@192.xxx.xxx.xxx:65001 \
    ritik@10.0.xxx.xxx
```

Once connected, access the application at: **http://localhost:3000**

---

## First Login

1. Navigate to **http://localhost:3000**
2. Click **Login**
3. Enter the default credentials:
   - **Username**: `admin`
   - **Password**: `admin123`
4. You're in! 🎉

**Change the default admin password immediately in production environments!**


## Docker Deployment

### Environment Setup

Use the deployment script at [install/build.sh](install/build.sh).

- On first run, the script copies `.env.example` to `.env`.
- Edit `.env` to set required values before building (by running the script once again):
  - `NEXT_PUBLIC_API_URL`
  - `FRONTEND_URL`
  - `MONGODB_URI`
  - `PDF_RESULTS_HOST_PATH`
  - `PDFS_HOST_PATH`


### Build and Run

```bash
cd AIComps/input-handlers/pdf/viewer/install

# Build and start all services via the script -> run twice if .env is not present
./build.sh

# Start services
docker compose up

# View logs
docker compose logs -f

# Stop services
docker compose down
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5001
- **Health Check**: http://localhost:5001/health
---

# Additional Documentation
## User Management
### Permission Model

```
User
 ├─ username, email, password
 ├─ role: 'admin' | 'user'
 └─ groups: [GroupId]
          │
          ▼
     UserGroup
          │
          ├─ name, description
          └─ permissions to Documents
                    │
                    ▼
                Document
                    │
                    ├─ documentId, name
                    └─ permissions: [GroupId]

Access Rule:
User can access Document IF:
  User.groupIds ∩ Document.permissions.groupIds ≠ ∅
```

### Complete Workflow Example - API Documentation

#### 1. Login as Admin

```bash
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

Save the `sessionToken` from the response.

#### 2. Create User Groups

```bash
ADMIN_TOKEN="your-session-token"

# Create Engineering group
curl -X POST http://localhost:5001/api/admin/groups \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Engineering",
    "description": "Engineering team members"
  }'

# Create Marketing group
curl -X POST http://localhost:5001/api/admin/groups \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Marketing",
    "description": "Marketing department"
  }'
```

Save the `groupId` for each group.

#### 3. Create Users

```bash
# Create user Alice
curl -X POST http://localhost:5001/api/admin/users \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "password": "AlicePass123"
  }'
```

#### 4. Assign Users to Groups

```bash
# Add Alice to Engineering group
curl -X POST http://localhost:5001/api/admin/users/ALICE_USER_ID/groups/ENGINEERING_GROUP_ID \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

#### 5. Grant Document Access

```bash
# Grant Engineering group access to BMRA-Single-Server
curl -X POST http://localhost:5001/api/admin/documents/BMRA-Single-Server/permissions \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "groupId": "ENGINEERING_GROUP_ID"
  }'
```

#### 6. Test User Access

```bash
# Login as Alice
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "AlicePass123"
  }'

# List documents Alice can see
curl -X GET http://localhost:5001/api/documents \
  -H "Authorization: Bearer ALICE_TOKEN"
```

Alice will only see documents that the Engineering group has access to.

## Admin Panel Guide

### Accessing the Admin Panel

1. Login with admin credentials
2. Click the "Admin" button in the dashboard header
3. Or navigate to `http://localhost:3000/admin`

### Admin Panel Features

#### 👥 Users Tab

**Create a New User:**
1. Click "Add User"
2. Fill in details:
   - Username (required, unique)
   - Email (required)
   - Full Name (optional)
   - Password (required)
   - Role (admin/user)
   - Groups (select one or more)
3. Click "Save"

**Edit User:**
- Click the edit (✏️) button
- Modify any field
- Change password (leave empty to keep current)
- Add/remove from groups
- Click "Save"

**Delete User:**
- Click the delete (🗑️) button
- Confirm deletion
- User will be soft-deleted (marked inactive)

#### 🛡️ Groups Tab

**Create Group:**
1. Click "Add Group"
2. Enter group name and description
3. Click "Save"

**Manage Groups:**
- Edit group name/description
- Delete groups (removes all permissions)
- View member count

#### 📄 Documents Tab

**Scan for New Documents:**
1. Click "Scan for Documents"
2. Review discovered documents
3. Click "Add" for each document to import

**Manage Permissions:**
1. Click on a document to expand it
2. Check groups that should have access
3. Uncheck to revoke access
4. Changes save automatically


## Troubleshooting

### Cannot connect to MongoDB

**Problem:** Backend fails to start with MongoDB connection error

**Solutions:**
1. Check MongoDB is running: `docker ps | grep doc-flow`
2. Verify connection string in `backend/src/config/database.ts`
3. Ensure MongoDB is accessible on port 27017

### Documents not appearing

**Problem:** Documents don't show up after scanning

**Solutions:**
1. Verify PDF output folders exist in `~/pdf-results/ervin/outputs/`
2. Run `npm run init-docs` to scan for new documents
3. Check file permissions on the outputs directory
4. Review backend logs for errors

## Common Workflows

### Onboard a New Team Member

1. **Create user account** (Admin Panel → Users → Add User)
2. **Assign to appropriate groups** (check groups during creation or edit later)
3. **User receives credentials** (communicate securely)
4. **User logs in** and accesses authorized documents

### Create a New Project Team

1. **Create group** (Admin Panel → Groups → Add Group)
   - Example: "Project Unnati"
2. **Assign users to group** (Admin Panel → Users → Edit → Check group)
3. **Grant document access** (Admin Panel → Documents → Expand → Check group)
4. **Team members can now access** project documents

### Add New Documents

1. **Process PDFs** (using your document processing pipeline)
2. **Scan for documents** (Admin Panel → Documents → Scan for Documents)
3. **Add discovered documents** (Click "Add" for each)
4. **Assign permissions** (Expand document → Check groups)


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

## Quick Start

### Prerequisites

- Node.js 22+
- MongoDB running on `localhost:27017`
- PDF processing results in `~/pdf-results` directory

### Installation Steps

```bash
# 1. Install backend dependencies
cd backend
npm install

# 2. Initialize admin user and group
npm run init-admin

# 3. Initialize documents with admin permissions
npm run init-docs

# 4. Start backend server
npm run dev
```

In a new terminal:

```bash
# 5. Install frontend dependencies
cd frontend
npm install

# 6. Configure environment
NEXT_PUBLIC_API_URL=http://10.0.224.193:5001

# 7. Start frontend
npm run dev
```

### First Login

1. Navigate to `http://localhost:3000`
2. Click "Login"
3. Enter credentials:
   - **Username**: `admin`
   - **Password**: `admin123`
4. You're in! 🎉

⚠️ **Important:** Change the default admin password immediately in production!


## Initial Setup - Development

### Step 1: Initialize Admin User

This creates the admin user and admin group:

```bash
cd backend
npm run init-admin
```

**Output:**
```
✅ Admin group created with ID: 692546aead66512cf9d88149
✅ Admin user created with ID: 692546aead66512cf9d8814a

⚠️  DEFAULT CREDENTIALS:
   Username: admin
   Password: admin123
```

### Step 2: Initialize Documents

This scans the outputs directory and creates document records:

```bash
npm run init-docs
```

**What this does:**
- Scans `/home/intel/pdf-results/ervin/outputs/` for document folders
- Creates a database record for each document
- Automatically grants the admin group access to all documents


### Step 3: Start Services

```bash
# Backend (in backend directory)
npm run dev  # Runs on http://localhost:5001

# Frontend (in frontend directory)
npm run dev  # Runs on http://localhost:3000
```

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

### Complete Workflow Example

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

## Docker Deployment

### Environment Setup

Create `.env` file in the install directory:

```env
# For local development
NEXT_PUBLIC_API_URL=http://localhost:5001
FRONTEND_URL=http://localhost:3000

# For server deployment (example)
# NEXT_PUBLIC_API_URL=http://10.0.224.193:5001
# FRONTEND_URL=http://10.0.224.193:3000
```

### Build and Run

```bash
cd install

# Build and start all services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5001
- **Health Check**: http://localhost:5001/health

### Production Deployment

For server deployment at a specific IP (e.g., 10.138.190.67):

```bash
# Create .env
cat > .env << EOF
NEXT_PUBLIC_API_URL=http://10.138.190.67:5001
FRONTEND_URL=http://10.138.190.67:3000
EOF

# Build with environment variables
docker-compose up --build -d
```

**Important:** `NEXT_PUBLIC_API_URL` is embedded at build time. To change it, you must rebuild the frontend image.

## Development

### Backend Development

```bash
cd backend

# Development mode with auto-reload
npm run dev

# Build TypeScript
npm run build

# Production mode
npm start

# Initialize admin
npm run init-admin

# Initialize documents
npm run init-docs
```

### Frontend Development

```bash
cd frontend

# Development mode
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Type checking
npm run type-check

# Linting
npm run lint
```

## Security

### Best Practices

1. **Change Default Passwords**
   - Immediately change the admin password after initialization
   - Use strong passwords (min 12 characters, mixed case, numbers, symbols)

2. **Environment Variables**
   - Never commit `.env` files
   - Use different credentials for development and production
   - Rotate session secrets regularly

3. **HTTPS in Production**
   - Always use HTTPS/TLS in production
   - Configure proper SSL certificates
   - Enable HSTS headers

4. **Session Management**
   - Sessions expire after 24 hours
   - Tokens are validated on every request
   - Auto-logout on token expiration

5. **Access Control**
   - Follow principle of least privilege
   - Regular audit of user permissions
   - Remove inactive users promptly


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
1. Verify PDF output folders exist in `/home/intel/pdf-results/ervin/outputs/`
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
   - Example: "Project Phoenix"
2. **Assign users to group** (Admin Panel → Users → Edit → Check group)
3. **Grant document access** (Admin Panel → Documents → Expand → Check group)
4. **Team members can now access** project documents

### Add New Documents

1. **Process PDFs** (using your document processing pipeline)
2. **Scan for documents** (Admin Panel → Documents → Scan for Documents)
3. **Add discovered documents** (Click "Add" for each)
4. **Assign permissions** (Expand document → Check groups)

### Audit User Access

1. **View user details** (`GET /api/admin/users/:userId`)
2. **Check group memberships** (shown in response)
3. **For each group, list documents** (`GET /api/admin/documents`)
4. **Filter by permissions.groupId** in the response

## Support

### Documentation Files

- This README - Complete system guide
- `backend/src/` - Backend source code with inline comments
- `frontend/app/` - Frontend pages and components


**Built with:** Node.js, TypeScript, Next.js, MongoDB, Express


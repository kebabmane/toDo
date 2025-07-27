#!/usr/bin/env python3
"""
Test script to simulate the exact frontend workflow
"""
import requests
import json

API_URL = 'http://localhost:5001'

def test_frontend_workflow():
    print("🔍 Testing Frontend Workflow")
    
    # 1. Login to get token
    print("\n1. Logging in...")
    login_response = requests.post(f'{API_URL}/auth/login', 
                                  json={'username': 'testuser123', 'password': 'password123'})
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
        return
        
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    print(f"✅ Login successful, token: {token[:50]}...")
    
    # 2. Get todo lists
    print("\n2. Getting todo lists...")
    lists_response = requests.get(f'{API_URL}/todolists', headers=headers)
    
    if lists_response.status_code != 200:
        print(f"❌ Get todo lists failed: {lists_response.status_code} - {lists_response.text}")
        return
        
    todo_lists = lists_response.json()
    print(f"✅ Found {len(todo_lists)} todo lists")
    
    if not todo_lists:
        print("⚠️ No todo lists found, creating one...")
        create_response = requests.post(f'{API_URL}/todolists', 
                                       json={'name': 'Test List'}, headers=headers)
        if create_response.status_code != 201:
            print(f"❌ Create list failed: {create_response.status_code} - {create_response.text}")
            return
        list_id = create_response.json()['id']
        print(f"✅ Created list ID: {list_id}")
    else:
        list_id = todo_lists[0]['id']
        print(f"✅ Using existing list ID: {list_id}")
    
    # 3. Get todos from list (initial fetch)
    print(f"\n3. Getting todos from list {list_id}...")
    todos_response = requests.get(f'{API_URL}/todolists/{list_id}/todos', headers=headers)
    
    if todos_response.status_code != 200:
        print(f"❌ Get todos failed: {todos_response.status_code} - {todos_response.text}")
        return
        
    todos_data = todos_response.json()
    todos = todos_data.get('todos', [])
    print(f"✅ Found {len(todos)} todos in list")
    
    # 4. Create a todo if none exist
    if not todos:
        print("\n4. Creating a test todo...")
        create_todo_response = requests.post(f'{API_URL}/todolists/{list_id}/todos',
                                           json={'title': 'Test frontend todo'}, headers=headers)
        
        if create_todo_response.status_code != 201:
            print(f"❌ Create todo failed: {create_todo_response.status_code} - {create_todo_response.text}")
            return
            
        todo_data = create_todo_response.json()
        todo_id = todo_data['todo']['id']
        print(f"✅ Created todo ID: {todo_id}")
    else:
        todo_id = todos[0]['id']
        print(f"✅ Using existing todo ID: {todo_id}")
    
    # 5. Update todo to mark as completed (this is where the issue occurs)
    print(f"\n5. Marking todo {todo_id} as completed...")
    update_response = requests.put(f'{API_URL}/todolists/{list_id}/todos/{todo_id}',
                                  json={'completed': True}, headers=headers)
    
    if update_response.status_code != 200:
        print(f"❌ Update todo failed: {update_response.status_code} - {update_response.text}")
        return
        
    print("✅ Todo marked as completed")
    print(f"   Response: {update_response.json()}")
    
    # 6. Fetch todos again (this is where the frontend fails)
    print(f"\n6. Fetching todos after update...")
    fetch_response = requests.get(f'{API_URL}/todolists/{list_id}/todos', headers=headers)
    
    if fetch_response.status_code != 200:
        print(f"❌ Fetch after update failed: {fetch_response.status_code} - {fetch_response.text}")
        print(f"   Headers: {dict(fetch_response.headers)}")
        return
        
    updated_todos_data = fetch_response.json()
    updated_todos = updated_todos_data.get('todos', [])
    print(f"✅ Successfully fetched {len(updated_todos)} todos after update")
    
    # Find our updated todo
    updated_todo = next((t for t in updated_todos if t['id'] == todo_id), None)
    if updated_todo:
        print(f"   Todo {todo_id} completed status: {updated_todo['completed']}")
    
    print("\n🎉 Complete workflow test passed!")

if __name__ == '__main__':
    try:
        test_frontend_workflow()
    except Exception as e:
        print(f"❌ Workflow test failed with exception: {e}")
        import traceback
        traceback.print_exc()
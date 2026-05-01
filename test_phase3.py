import os
import io
from app import app, db, User, Handout, Query, Response, FilterLog

def test_phase3():
    print("=== Phase 3: Integration & API Verification ===\n")
    
    client = app.test_client()
    app.config['TESTING'] = True
    
    with app.app_context():
        # 1. Setup - Create a test instructor and student
        admin = User.query.filter_by(role='admin').first()
        student = User.query.filter_by(role='student').first()
        
        if not admin or not student:
            print("  - [Error] Need admin and student in DB to test. Run app.py first.")
            return

        # 2. Test Handout Upload
        print("1. Testing Handout Upload (/upload_handout)...")
        with client.session_transaction() as sess:
            sess['user_id'] = admin.id
            sess['role']    = admin.role
            sess['name']    = admin.name
            
        data = {
            'file': (io.BytesIO(b"%PDF-1.4\n1 0 obj\n<< /Title (Test) >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"), 'test.pdf')
        }
        # Note: PyPDF2 might fail on this empty PDF, but let's see if the route logic works
        # For a better test, we can use the existing 'user manual.pdf'
        manual_path = os.path.join(os.path.dirname(__file__), "user manual.pdf")
        if os.path.exists(manual_path):
            with open(manual_path, 'rb') as f:
                data = {'file': (io.BytesIO(f.read()), 'test_manual.pdf')}
        
        response = client.post('/upload_handout', data=data, content_type='multipart/form-data', follow_redirects=True)
        if b'uploaded and processed successfully' in response.data:
            print("  - [PASS] Handout uploaded and stored in DB.")
        else:
            print(f"  - [FAIL] Handout upload failed. Response: {response.status_code}")

        # 3. Test Academic Filter Rejection
        print("\n2. Testing Query Analysis - Rejection (/analyze_query)...")
        with client.session_transaction() as sess:
            sess['user_id'] = student.id
            sess['role']    = student.role
            
        response = client.post('/analyze_query', data={'query': 'i am present sir'})
        json_data = response.get_json()
        if json_data and not json_data.get('is_academic'):
            print(f"  - [PASS] Query rejected: {json_data.get('reason')}")
        else:
            print(f"  - [FAIL] Query not rejected. Response: {json_data}")

        # 4. Test Academic Query Success
        print("\n3. Testing Query Analysis - Success (/analyze_query)...")
        response = client.post('/analyze_query', data={'query': 'Explain primary memory'})
        json_data = response.get_json()
        if json_data and json_data.get('is_academic'):
            print(f"  - [PASS] Query accepted.")
            print(f"  - Keywords: {json_data.get('keywords')}")
            print(f"  - AI Response: {json_data.get('response')[:100]}...")
        else:
            print(f"  - [FAIL] Query failed or rejected. Response: {json_data}")

        # 5. Test History
        print("\n4. Testing History (/history)...")
        response = client.get('/history')
        json_data = response.get_json()
        if json_data and len(json_data) >= 1:
            print(f"  - [PASS] History retrieved {len(json_data)} interactions.")
        else:
            print(f"  - [FAIL] History empty or failed. Response: {response.status_code}")

    print("\n=== Verification Complete ===")

if __name__ == "__main__":
    test_phase3()

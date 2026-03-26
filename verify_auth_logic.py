from backend.auth import verify_password, get_password_hash
import sqlite3

def verify_admin():
    conn = sqlite3.connect('leitor_inteligente_v2.db')
    cursor = conn.cursor()
    cursor.execute("SELECT hashed_password FROM usuarios WHERE username='admin'")
    res = cursor.fetchone()
    if not res:
        print("User admin not found in DB")
        return
    
    hashed = res[0]
    password_to_test = "admin"
    is_correct = verify_password(password_to_test, hashed)
    print(f"Testing password '{password_to_test}' against hash: {is_correct}")
    
    # Also test creating a new hash and verifying it
    new_hash = get_password_hash("test123")
    print(f"Test verify new hash: {verify_password('test123', new_hash)}")

if __name__ == "__main__":
    verify_admin()

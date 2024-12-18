db.createUser({
    user: 'admin',
    pwd: 'password123',
    roles: [
      {
        role: 'readWrite',
        db: 'vulnerabilities'
      }
    ]
  });
  
  db.createCollection('node_vulnerabilities');
  db.createCollection('python_vulnerabilities');
  
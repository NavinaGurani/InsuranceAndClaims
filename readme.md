What changed:

Before	                                                                After
20+ files across db/, models/, repositories/, services/, core/, api/	4 files flat in app/
SQLAlchemy + asyncpg + PostgreSQL + Docker	                            Zero DB dependencies
JWT auth with bcrypt + python-jose	                                    Simple ?user_id=1 query param
15 packages in requirements.txt	                                        3 packages
Needs docker-compose up to run	                                        Just uvicorn app.main:app --reload

To run: uvicorn app.main:app --reload 
Swagger Link : hit /docs for the Swagger UI.

Mock users for testing:
?user_id=1 → admin (full access)
?user_id=2 → agent (can review claims)
?user_id=3 or 4 → customer (own data only)

[sample endpoint](http://127.0.0.1:8000/api/v1/users?user_id=1)

Adding some random text to view the changes
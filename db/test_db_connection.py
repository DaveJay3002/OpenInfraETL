from sqlalchemy.orm import sessionmaker
from models import Promoter, Project
from database import engine, init

# Initialize DB schema (creates tables)
init()

Session = sessionmaker(bind=engine)
session = Session()

# Create a promoter
promoter = Promoter(name="M/S. NEELACHAL INFRA DEVELOPERS PVT. LTD")
session.add(promoter)
session.commit()

# Create a project linked to promoter
project = Project(
    name="Basanti Enclave",
    rera_id="RP/01/2025/01362",
    address="Angul",
    promoter_id=promoter.id,
)
session.add(project)
session.commit()

# Query back to verify
result = session.query(Project).filter_by(name="Basanti Enclave").first()
print(f"Project: {result.name}, RERA: {result.rera_id}, Address: {result.address}")
print(f"Promoter: {result.promoter.name}")

# Close session
session.close()

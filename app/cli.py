from __future__ import annotations

from datetime import UTC, datetime
import random

import click
from flask import current_app
from werkzeug.security import generate_password_hash

from .constants import ROLES
from .extensions import db
from .models import Candidate, Client, Job, Role, User


@click.command("init-db")
def init_db_command():
    db.create_all()
    _seed_roles()
    click.echo("Database initialized and roles seeded.")


@click.command("create-owner")
@click.option("--username", prompt=True)
@click.option("--full-name", prompt=True)
@click.option("--email", prompt=False, default="")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
def create_owner_command(username: str, full_name: str, email: str, password: str):
    _create_user_with_role("owner", username, full_name, email or None, password)
    click.echo(f"Owner user {username} created.")


@click.command("create-admin")
@click.option("--username", prompt=True)
@click.option("--full-name", prompt=True)
@click.option("--email", prompt=False, default="")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
def create_admin_command(username: str, full_name: str, email: str, password: str):
    _create_user_with_role("admin", username, full_name, email or None, password)
    click.echo(f"Admin user {username} created.")


@click.command("create-user")
@click.option("--role", prompt=True, type=click.Choice(ROLES))
@click.option("--username", prompt=True)
@click.option("--full-name", prompt=True)
@click.option("--email", prompt=False, default="")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
def create_user_command(
    role: str,
    username: str,
    full_name: str,
    email: str,
    password: str,
):
    _create_user_with_role(role, username, full_name, email or None, password)
    click.echo(f"{role.title()} user {username} created.")


@click.command("seed-demo-data")
def seed_demo_data_command():
    from datetime import timedelta
    import random
    from .models import (
        ActivityLog, CandidateStatusHistory, Employee, EmployeeProject,
        Note, Project, Submission, SubmissionStatusHistory, Task, Timesheet
    )
    
    _seed_roles()

    # Create users with different roles (30+ users)
    owner_role = Role.query.filter_by(name="owner").first()
    admin_role = Role.query.filter_by(name="admin").first()
    recruiter_role = Role.query.filter_by(name="recruiter").first()
    hr_role = Role.query.filter_by(name="hr").first()
    employee_role = Role.query.filter_by(name="employee").first()

    first_names = ["Sarah", "Mike", "Emily", "Robert", "Jessica", "David", "Amanda", "Chris", "Lisa", "James",
                   "Maria", "John", "Jennifer", "Michael", "Linda", "William", "Patricia", "Richard", "Barbara", "Joseph",
                   "Susan", "Thomas", "Karen", "Charles", "Nancy", "Daniel", "Betty", "Matthew", "Margaret", "Anthony",
                   "Sandra", "Mark", "Ashley", "Donald", "Dorothy"]
    
    last_names = ["Johnson", "Chen", "Davis", "Wilson", "Martinez", "Anderson", "Taylor", "Thomas", "Moore", "Jackson",
                  "Martin", "Lee", "Thompson", "White", "Harris", "Clark", "Lewis", "Robinson", "Walker", "Young",
                  "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green", "Adams",
                  "Nelson", "Baker", "Hall", "Rivera", "Campbell"]

    users_data = []
    # Add specific key users
    users_data.extend([
        ("recruiter1", "Sarah Johnson", "sarah.j@jupiter.tech", recruiter_role),
        ("recruiter2", "Mike Chen", "mike.c@jupiter.tech", recruiter_role),
        ("hr1", "Emily Davis", "emily.d@jupiter.tech", hr_role),
        ("hr2", "Robert Wilson", "robert.w@jupiter.tech", hr_role),
        ("admin1", "Jessica Martinez", "jessica.m@jupiter.tech", admin_role),
    ])
    
    # Generate additional users to reach 30+
    role_distribution = [recruiter_role] * 15 + [hr_role] * 8 + [admin_role] * 5 + [employee_role] * 7
    for i in range(5, 35):
        first = first_names[i % len(first_names)]
        last = last_names[i % len(last_names)]
        username = f"user{i}"
        email = f"{first.lower()}.{last.lower()}{i}@jupiter.tech"
        role = role_distribution[i % len(role_distribution)]
        users_data.append((username, f"{first} {last}", email, role))

    users = {}
    for username, full_name, email, role in users_data:
        user = User.query.filter_by(username=username).first()
        if user is None:
            user = User(
                username=username,
                full_name=full_name,
                email=email,
                password_hash=generate_password_hash("password123"),
                role_id=role.id,
            )
            db.session.add(user)
            db.session.flush()
        users[username] = user

    recruiter1 = users["recruiter1"]
    recruiter2 = users["recruiter2"]
    hr1 = users["hr1"]
    all_users = list(users.values())

    # Create clients (30+)
    company_prefixes = ["Tech", "Global", "Advanced", "Premier", "Elite", "Dynamic", "Innovative", "Strategic", "Digital", "Smart"]
    company_types = ["Solutions", "Systems", "Group", "Innovations", "Technologies", "Enterprises", "Corporation", "Industries", "Partners", "Consulting"]
    industries = ["Tech", "Finance", "Healthcare", "Retail", "Education", "Manufacturing", "Logistics", "Media", "Energy", "Telecom"]
    
    cities = [
        ("San Francisco", "CA"), ("New York", "NY"), ("Boston", "MA"), ("Chicago", "IL"), ("Austin", "TX"),
        ("Seattle", "WA"), ("Denver", "CO"), ("Atlanta", "GA"), ("Miami", "FL"), ("Portland", "OR"),
        ("Phoenix", "AZ"), ("San Diego", "CA"), ("Dallas", "TX"), ("Houston", "TX"), ("Philadelphia", "PA"),
        ("Los Angeles", "CA"), ("Detroit", "MI"), ("Minneapolis", "MN"), ("Charlotte", "NC"), ("Nashville", "TN"),
        ("Las Vegas", "NV"), ("Columbus", "OH"), ("Indianapolis", "IN"), ("San Antonio", "TX"), ("Sacramento", "CA"),
        ("Kansas City", "MO"), ("Milwaukee", "WI"), ("Baltimore", "MD"), ("Raleigh", "NC"), ("Tampa", "FL"),
        ("Orlando", "FL"), ("Cleveland", "OH"), ("Pittsburgh", "PA"), ("Cincinnati", "OH"), ("Salt Lake City", "UT")
    ]

    clients = []
    for idx in range(1, 36):
        company = f"{company_prefixes[idx % len(company_prefixes)]} {company_types[idx % len(company_types)]}"
        if idx <= 5:
            company = ["TechCorp Solutions", "Global Finance Inc", "HealthCare Systems", "RetailMax Group", "EduTech Innovations"][idx-1]
        
        contact_first = first_names[(idx * 2) % len(first_names)]
        contact_last = last_names[(idx * 3) % len(last_names)]
        contact = f"{contact_first} {contact_last}"
        email = f"{contact_first.lower()}.{contact_last.lower()}@{company.lower().replace(' ', '')}.com"
        phone = f"555-{1000 + idx:04d}"
        city, state = cities[idx % len(cities)]
        address = f"{100 + idx * 10} Business Blvd, {city}, {state}"
        
        client = Client.query.filter_by(client_code=f"CL{idx:04d}").first()
        if client is None:
            client = Client(
                client_code=f"CL{idx:04d}",
                company_name=company,
                contact_person=contact,
                email=email,
                phone=phone,
                address=address,
                is_active=idx <= 32,  # Make a few inactive
                created_by=all_users[idx % len(all_users)].id,
                updated_by=all_users[idx % len(all_users)].id,
            )
            db.session.add(client)
            db.session.flush()
        clients.append(client)

    # Create jobs with various statuses (40+)
    job_titles = [
        "Senior Python Developer", "React Frontend Engineer", "DevOps Engineer", "Data Scientist", "Java Backend Developer",
        "QA Automation Engineer", "Product Manager", "UI/UX Designer", "Full Stack Developer", "Mobile Developer",
        "Cloud Architect", "Security Engineer", "Machine Learning Engineer", "Business Analyst", "Scrum Master",
        "Technical Writer", "Database Administrator", "Network Engineer", "Systems Administrator", "Site Reliability Engineer",
        "Angular Developer", "Vue.js Developer", "iOS Developer", "Android Developer", "Flutter Developer",
        "Salesforce Developer", ".NET Developer", "PHP Developer", "Ruby Developer", "Go Developer",
        "Data Engineer", "ETL Developer", "BI Developer", "Frontend Architect", "Backend Architect",
        "Solutions Architect", "Integration Specialist", "API Developer", "Blockchain Developer", "Game Developer"
    ]
    
    skills_list = [
        "Python, Django, PostgreSQL", "React, TypeScript, Redux", "AWS, Kubernetes, Terraform", "Python, ML, TensorFlow",
        "Java, Spring Boot, Microservices", "Selenium, Python, CI/CD", "Agile, Product Strategy", "Figma, Adobe XD, User Research",
        "Node.js, React, MongoDB", "React Native, iOS, Android", "Azure, GCP, Cloud Architecture", "Security, Penetration Testing",
        "PyTorch, Deep Learning, NLP", "SQL, Tableau, Requirements", "Jira, Confluence, Agile", "Documentation, API Docs",
        "MySQL, Oracle, Performance Tuning", "Cisco, Routing, Switching", "Linux, Windows Server, VMware", "Monitoring, Incident Response",
        "Angular, RxJS, NgRx", "Vue.js, Vuex, Nuxt", "Swift, UIKit, SwiftUI", "Kotlin, Jetpack, MVVM", "Dart, Flutter, Firebase",
        "Apex, Visualforce, Lightning", "C#, ASP.NET, Entity Framework", "PHP, Laravel, MySQL", "Ruby on Rails, PostgreSQL",
        "Golang, Microservices, gRPC", "Spark, Airflow, Kafka", "Informatica, SSIS, Data Warehousing", "Power BI, DAX, SQL",
        "HTML, CSS, JavaScript, Responsive", "Microservices, REST, GraphQL", "AWS, Solution Design, Migration",
        "MuleSoft, API Gateway, ESB", "REST, GraphQL, API Design", "Solidity, Web3, Smart Contracts", "Unity, C#, Game Design"
    ]
    
    statuses = ["open"] * 25 + ["filled"] * 5 + ["on_hold"] * 5 + ["closed"] * 5
    emp_types = ["Full-time"] * 25 + ["Contract"] * 10 + ["Part-time"] * 5
    work_locations = ["Remote"] * 10 + [f"{city}, {state}" for city, state in cities[:30]]

    jobs = []
    for idx in range(1, 41):
        title = job_titles[(idx - 1) % len(job_titles)]
        client = clients[(idx - 1) % len(clients)]
        status = statuses[(idx - 1) % len(statuses)]
        location = work_locations[(idx - 1) % len(work_locations)]
        emp_type = emp_types[(idx - 1) % len(emp_types)]
        skills = skills_list[(idx - 1) % len(skills_list)]
        min_exp = random.randint(2, 5)
        max_exp = min_exp + random.randint(3, 7)
        
        if emp_type == "Contract":
            salary = f"${random.randint(60, 120)}/hr"
        else:
            salary = f"${random.randint(80, 180)}k-{random.randint(100, 220)}k"
        
        job = Job.query.filter_by(job_code=f"JOB{idx:04d}").first()
        if job is None:
            job = Job(
                job_code=f"JOB{idx:04d}",
                client_id=client.id,
                title=title,
                location=location,
                work_type="Remote" if "Remote" in location else "Onsite",
                employment_type=emp_type,
                required_skills=skills,
                min_experience=min_exp,
                max_experience=max_exp,
                salary_or_rate=salary,
                status=status,
                owner_user_id=all_users[idx % len(all_users)].id,
                description=f"We are seeking an experienced {title} to join our dynamic team. This role offers exciting challenges and growth opportunities.",
                created_by=all_users[idx % len(all_users)].id,
                updated_by=all_users[idx % len(all_users)].id,
            )
            db.session.add(job)
            db.session.flush()
        jobs.append(job)

    # Create candidates with various statuses (50+)
    candidate_statuses = ["new", "screening", "interview", "submitted", "selected", "joined", "rejected", "on_hold"]
    skill_sets = [
        "Python, Django, REST APIs", "React, JavaScript, CSS", "Java, Spring, Microservices", "AWS, Docker, Kubernetes",
        "Node.js, Express, MongoDB", "Python, ML, TensorFlow", "UI/UX, Figma, Design Systems", "QA, Selenium, Automation",
        "Full Stack, React, Node.js", "Mobile, React Native, iOS", "Data Science, Python, SQL", "DevOps, CI/CD, Jenkins",
        "Angular, TypeScript, RxJS", "Vue.js, Vuex, JavaScript", "C#, .NET, Azure", "PHP, Laravel, MySQL",
        "Ruby on Rails, PostgreSQL", "Go, Microservices, gRPC", "Swift, iOS, UIKit", "Kotlin, Android, MVVM",
        "Flutter, Dart, Firebase", "Salesforce, Apex, Lightning", "SAP, ABAP, Fiori", "Oracle, PL/SQL, Database",
        "Tableau, Power BI, Analytics", "Spark, Hadoop, Big Data", "Terraform, Ansible, IaC", "Security, Penetration Testing",
        "Blockchain, Solidity, Web3", "Unity, C#, Game Development", "Unreal Engine, C++, Graphics", "Embedded, C, IoT",
        "COBOL, Mainframe, Legacy", "Perl, Shell Scripting, Linux", "R, Statistics, Data Analysis"
    ]
    
    sources = ["LinkedIn", "Indeed", "Referral", "Company Website", "Recruiter Contact", "Job Board", "Career Fair", "Agency"]

    candidates = []
    for idx in range(1, 56):
        first = first_names[idx % len(first_names)]
        last = last_names[(idx * 2) % len(last_names)]
        email = f"{first.lower()}.{last.lower()}{idx}@email.com"
        phone = f"555-{2000 + idx:04d}"
        city, state = cities[idx % len(cities)]
        location = f"{city}, {state}"
        skills = skill_sets[idx % len(skill_sets)]
        exp = random.randint(1, 15)
        source = sources[idx % len(sources)]
        status = candidate_statuses[idx % len(candidate_statuses)]
        
        candidate = Candidate.query.filter_by(email=email).first()
        if candidate is None:
            candidate = Candidate(
                candidate_code=f"CAN{idx:04d}",
                first_name=first,
                last_name=last,
                full_name=f"{first} {last}",
                email=email,
                phone=phone,
                location=location,
                primary_skills=skills,
                years_experience=exp,
                source=source,
                status=status,
                owner_user_id=all_users[idx % len(all_users)].id,
                notes_summary=f"Candidate with {exp} years of experience in {skills.split(',')[0]}",
                created_by=all_users[idx % len(all_users)].id,
                updated_by=all_users[idx % len(all_users)].id,
            )
            db.session.add(candidate)
            db.session.flush()
        candidates.append(candidate)

    # Create submissions with various statuses (40+)
    submission_statuses = ["submitted", "interview", "selected", "joined", "rejected", "withdrawn"]
    
    submissions = []
    for idx in range(min(40, len(candidates), len(jobs))):
        candidate = candidates[idx]
        job = jobs[idx % len(jobs)]
        
        # Check if submission already exists
        existing = Submission.query.filter_by(candidate_id=candidate.id, job_id=job.id).first()
        if existing:
            submissions.append(existing)
            continue
            
        status = submission_statuses[idx % len(submission_statuses)]
        interview_date = None
        if status == "interview":
            interview_date = datetime.now(UTC) + timedelta(days=random.randint(1, 14))
        
        submission = Submission(
            candidate_id=candidate.id,
            job_id=job.id,
            recruiter_user_id=all_users[idx % len(all_users)].id,
            status=status,
            interview_date=interview_date,
            feedback=f"Candidate shows {'strong' if idx % 3 == 0 else 'good'} potential for {job.title} position.",
            created_by=all_users[idx % len(all_users)].id,
            updated_by=all_users[idx % len(all_users)].id,
        )
        db.session.add(submission)
        db.session.flush()
        submissions.append(submission)

    # Create employees (converted from candidates) (30+)
    employment_types = ["Full-time", "Contract", "Part-time"]
    employee_statuses = ["active", "on_leave", "terminated"]
    
    employees = []
    for idx in range(min(35, len(candidates))):
        candidate = candidates[idx]
        
        # Check if employee already exists
        existing = Employee.query.filter_by(candidate_id=candidate.id).first()
        if existing:
            employees.append(existing)
            continue
        
        # Only create employees for candidates with "joined" or "selected" status
        if idx % 5 == 0 or candidate.status in ["joined", "selected"]:
            emp_code = f"EMP{len(employees) + 1:04d}"
            client = clients[idx % len(clients)]
            start_date = datetime.now(UTC).date() - timedelta(days=random.randint(30, 365))
            emp_type = employment_types[idx % len(employment_types)]
            status = employee_statuses[idx % len(employee_statuses)] if idx % 10 != 0 else "active"
            
            employee = Employee(
                employee_code=emp_code,
                candidate_id=candidate.id,
                full_name=candidate.full_name,
                email=candidate.email,
                phone=candidate.phone,
                client_id=client.id,
                start_date=start_date,
                end_date=None if status == "active" else start_date + timedelta(days=random.randint(180, 540)),
                employment_type=emp_type,
                reporting_manager=f"{first_names[idx % len(first_names)]} {last_names[(idx+1) % len(last_names)]}",
                status=status,
                billing_status="active" if status == "active" else "inactive",
                created_by=hr1.id,
                updated_by=hr1.id,
            )
            db.session.add(employee)
            db.session.flush()
            employees.append(employee)

    # Create projects (30+)
    project_statuses = ["active", "completed", "on_hold", "cancelled"]
    project_names = [
        "Platform Redesign", "Portal Development", "API Migration", "Mobile App Launch", "Cloud Migration",
        "Data Warehouse Implementation", "Security Audit", "Performance Optimization", "Legacy System Modernization",
        "Customer Portal", "Analytics Dashboard", "Payment Gateway Integration", "Microservices Architecture",
        "DevOps Transformation", "AI/ML Integration", "Blockchain Implementation", "IoT Platform", "CRM Integration",
        "ERP Upgrade", "Website Redesign", "Mobile Banking App", "E-commerce Platform", "Supply Chain System",
        "HR Management System", "Inventory Management", "Business Intelligence", "Marketing Automation",
        "Customer Service Portal", "Document Management", "Compliance System", "Reporting Framework",
        "Integration Platform", "Testing Automation", "Infrastructure Upgrade", "Disaster Recovery"
    ]

    projects = []
    for idx in range(1, 36):
        client = clients[idx % len(clients)]
        proj_code = f"PRJ{idx:04d}"
        name = f"{client.company_name.split()[0]} {project_names[idx % len(project_names)]}"
        
        start_date = datetime.now(UTC).date() - timedelta(days=random.randint(30, 730))
        duration = random.randint(90, 365)
        end_date = start_date + timedelta(days=duration)
        status = project_statuses[idx % len(project_statuses)]
        
        project = Project.query.filter_by(project_code=proj_code).first()
        if project is None:
            project = Project(
                project_code=proj_code,
                client_id=client.id,
                project_name=name,
                start_date=start_date,
                end_date=end_date,
                status=status,
                notes=f"Strategic project for {client.company_name} focusing on digital transformation.",
                created_by=all_users[idx % len(all_users)].id,
                updated_by=all_users[idx % len(all_users)].id,
            )
            db.session.add(project)
            db.session.flush()
        projects.append(project)

    # Assign employees to projects (40+ assignments)
    for idx in range(min(45, len(employees), len(projects))):
        employee = employees[idx % len(employees)]
        project = projects[idx % len(projects)]
        
        emp_proj = EmployeeProject.query.filter_by(employee_id=employee.id, project_id=project.id).first()
        if emp_proj is None:
            assigned_from = employee.start_date + timedelta(days=random.randint(0, 30))
            emp_proj = EmployeeProject(
                employee_id=employee.id,
                project_id=project.id,
                assigned_from=assigned_from,
                assigned_to=assigned_from + timedelta(days=random.randint(90, 365)) if idx % 5 == 0 else None,
                status="active" if idx % 7 != 0 else "completed",
                notes=f"Assigned to {project.project_name}",
            )
            db.session.add(emp_proj)

    # Create timesheets (50+)
    timesheet_statuses = ["draft", "submitted", "approved", "rejected", "pending"]
    
    if len(employees) > 0:
        for idx in range(min(55, len(employees) * 3)):
            employee = employees[idx % len(employees)]
            
            # Generate week ranges
            weeks_ago = idx // len(employees)
            week_start = datetime.now(UTC).date() - timedelta(days=weeks_ago * 7 + datetime.now(UTC).weekday())
            week_end = week_start + timedelta(days=6)
            
            ts = Timesheet.query.filter_by(
                employee_id=employee.id,
                week_start=week_start
            ).first()
            
            if ts is None:
                hours = random.choice([35, 37.5, 40, 42, 45])
                status = timesheet_statuses[idx % len(timesheet_statuses)]
                
                ts = Timesheet(
                    employee_id=employee.id,
                    week_start=week_start,
                    week_end=week_end,
                    total_hours=hours,
                    status=status,
                    submitted_at=datetime.now(UTC) - timedelta(days=random.randint(1, 7)) if status != "draft" else None,
                    reviewed_by=hr1.id if status in ["approved", "rejected"] else None,
                    reviewed_at=datetime.now(UTC) - timedelta(days=random.randint(0, 5)) if status in ["approved", "rejected"] else None,
                    review_comments="Approved" if status == "approved" else ("Needs correction" if status == "rejected" else None),
                )
                db.session.add(ts)

    # Create tasks (50+)
    task_priorities = ["low", "medium", "high", "urgent"]
    task_statuses = ["open", "in_progress", "completed", "overdue", "cancelled"]
    task_titles = [
        "Follow up with candidate", "Schedule interview", "Review timesheet", "Update job posting",
        "Send offer letter", "Client check-in", "Prepare contract", "Conduct reference check",
        "Update candidate status", "Review resume", "Schedule technical interview", "Send rejection email",
        "Process onboarding", "Update project status", "Review employee performance", "Approve timesheet",
        "Create job description", "Post job on LinkedIn", "Screen candidates", "Coordinate interview panel",
        "Prepare offer package", "Negotiate salary", "Complete background check", "Setup employee accounts",
        "Conduct orientation", "Review project deliverables", "Update client on progress", "Prepare invoice",
        "Follow up on payment", "Schedule team meeting", "Review contract terms", "Update documentation",
        "Prepare status report", "Conduct exit interview", "Process termination", "Archive employee records"
    ]
    
    entity_types = ["candidate", "job", "submission", "employee", "client", "project", "general"]
    
    for idx in range(1, 56):
        entity_type = entity_types[idx % len(entity_types)]
        entity_id = None
        
        if entity_type == "candidate" and len(candidates) > 0:
            entity_id = candidates[idx % len(candidates)].id
        elif entity_type == "job" and len(jobs) > 0:
            entity_id = jobs[idx % len(jobs)].id
        elif entity_type == "submission" and len(submissions) > 0:
            entity_id = submissions[idx % len(submissions)].id
        elif entity_type == "employee" and len(employees) > 0:
            entity_id = employees[idx % len(employees)].id
        elif entity_type == "client" and len(clients) > 0:
            entity_id = clients[idx % len(clients)].id
        elif entity_type == "project" and len(projects) > 0:
            entity_id = projects[idx % len(projects)].id
        
        title = task_titles[idx % len(task_titles)]
        priority = task_priorities[idx % len(task_priorities)]
        status = task_statuses[idx % len(task_statuses)]
        
        # Create some overdue tasks
        if idx % 8 == 0:
            due_date = datetime.now(UTC).date() - timedelta(days=random.randint(1, 10))
            status = "overdue"
        else:
            due_date = datetime.now(UTC).date() + timedelta(days=random.randint(-5, 20))
        
        task = Task.query.filter_by(title=f"{title} #{idx}").first()
        if task is None:
            task = Task(
                title=f"{title} #{idx}",
                description=f"Task related to {entity_type}: {title}",
                entity_type=entity_type,
                entity_id=entity_id,
                assigned_user_id=all_users[idx % len(all_users)].id,
                priority=priority,
                due_date=due_date,
                status=status,
                created_by=all_users[(idx + 1) % len(all_users)].id,
                updated_by=all_users[(idx + 1) % len(all_users)].id,
            )
            db.session.add(task)

    # Create notes (60+)
    note_types = ["internal", "client", "interview", "reference"]
    note_contents = [
        "Strong technical skills, good cultural fit",
        "Client feedback: Excellent communication skills",
        "Needs improvement in problem-solving",
        "Very interested in the role and company",
        "Salary expectations align with budget",
        "Available to start immediately",
        "Requires visa sponsorship",
        "Prefers remote work arrangement",
        "Has competing offers, need to move quickly",
        "Reference check completed - all positive",
        "Technical interview scheduled for next week",
        "Candidate withdrew from process",
        "Client requested additional candidates",
        "Urgent requirement, prioritize submissions",
        "Budget approved for this position",
        "Interview feedback: Strong technical skills",
        "Soft skills need development",
        "Great team player, highly recommended",
        "Concerns about long-term commitment",
        "Excellent problem-solving abilities"
    ]
    
    for idx in range(1, 66):
        entity_type = entity_types[idx % len(entity_types)]
        entity_id = None
        
        if entity_type == "candidate" and len(candidates) > 0:
            entity_id = candidates[idx % len(candidates)].id
        elif entity_type == "job" and len(jobs) > 0:
            entity_id = jobs[idx % len(jobs)].id
        elif entity_type == "submission" and len(submissions) > 0:
            entity_id = submissions[idx % len(submissions)].id
        elif entity_type == "employee" and len(employees) > 0:
            entity_id = employees[idx % len(employees)].id
        elif entity_type == "client" and len(clients) > 0:
            entity_id = clients[idx % len(clients)].id
        elif entity_type == "project" and len(projects) > 0:
            entity_id = projects[idx % len(projects)].id
        else:
            continue
        
        note_type = note_types[idx % len(note_types)]
        content = note_contents[idx % len(note_contents)]
        
        note = Note.query.filter_by(entity_type=entity_type, entity_id=entity_id, content=content).first()
        if note is None:
            note = Note(
                entity_type=entity_type,
                entity_id=entity_id,
                note_type=note_type,
                content=content,
                created_by=all_users[idx % len(all_users)].id,
                created_at=datetime.now(UTC) - timedelta(days=random.randint(0, 30)),
            )
            db.session.add(note)

    # Create activity logs (100+)
    action_types = ["create", "update", "delete", "view", "approve", "reject", "submit"]
    
    for idx in range(1, 106):
        entity_type = entity_types[idx % len(entity_types)]
        entity_id = None
        action = action_types[idx % len(action_types)]
        
        if entity_type == "candidate" and len(candidates) > 0:
            entity_id = candidates[idx % len(candidates)].id
            message = f"{action.title()} candidate: {candidates[idx % len(candidates)].full_name}"
        elif entity_type == "job" and len(jobs) > 0:
            entity_id = jobs[idx % len(jobs)].id
            message = f"{action.title()} job: {jobs[idx % len(jobs)].title}"
        elif entity_type == "submission" and len(submissions) > 0:
            entity_id = submissions[idx % len(submissions)].id
            message = f"{action.title()} submission for job"
        elif entity_type == "employee" and len(employees) > 0:
            entity_id = employees[idx % len(employees)].id
            message = f"{action.title()} employee: {employees[idx % len(employees)].full_name}"
        elif entity_type == "client" and len(clients) > 0:
            entity_id = clients[idx % len(clients)].id
            message = f"{action.title()} client: {clients[idx % len(clients)].company_name}"
        elif entity_type == "project" and len(projects) > 0:
            entity_id = projects[idx % len(projects)].id
            message = f"{action.title()} project: {projects[idx % len(projects)].project_name}"
        else:
            continue
        
        log = ActivityLog.query.filter_by(entity_type=entity_type, entity_id=entity_id, action_type=action).first()
        if log is None:
            log = ActivityLog(
                user_id=all_users[idx % len(all_users)].id,
                action_type=action,
                entity_type=entity_type,
                entity_id=entity_id,
                message=message,
                created_at=datetime.now(UTC) - timedelta(days=random.randint(0, 60)),
            )
            db.session.add(log)

    db.session.commit()
    click.echo("Comprehensive demo data with 30+ records per entity seeded successfully!")


def _seed_roles() -> None:
    for role_name in ROLES:
        role = Role.query.filter_by(name=role_name).first()
        if role is None:
            role = Role(name=role_name, description=f"{role_name.title()} role")
            db.session.add(role)
    db.session.commit()


def _create_user_with_role(
    role_name: str,
    username: str,
    full_name: str,
    email: str | None,
    password: str,
) -> None:
    _seed_roles()

    if User.query.filter_by(username=username).first() is not None:
        raise click.ClickException("Username already exists.")

    if email and User.query.filter_by(email=email).first() is not None:
        raise click.ClickException("Email already exists.")

    role = Role.query.filter_by(name=role_name).first()
    user = User(
        username=username,
        full_name=full_name,
        email=email,
        password_hash=generate_password_hash(password),
        role_id=role.id,
    )
    db.session.add(user)
    db.session.commit()


def register_cli_commands(app):
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_owner_command)
    app.cli.add_command(create_admin_command)
    app.cli.add_command(create_user_command)
    app.cli.add_command(seed_demo_data_command)

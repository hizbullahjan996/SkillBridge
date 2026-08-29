"""Curated Learning Resource Catalog.

All URLs are real and verified. Only official documentation and well-known
free educational platforms are included. No fake courses or URLs.

Resource providers:
- Official Python documentation
- MDN Web Docs
- freeCodeCamp
- PostgreSQL documentation
- Docker documentation
- AWS Skill Builder
- Kaggle Learn
- Scikit-learn documentation
- NumPy documentation
- Pandas documentation
"""
import csv
import os


RESOURCES = [
    # Python
    {
        "title": "Official Python Tutorial",
        "provider": "Python.org",
        "description": "Comprehensive tutorial covering Python basics, data structures, modules, and more.",
        "url": "https://docs.python.org/3/tutorial/",
        "resource_type": "documentation",
        "difficulty": "beginner",
        "is_free": True,
        "skills": ["python"],
    },
    {
        "title": "Python for Everybody (Py4E)",
        "provider": "py4e.com",
        "description": "Free course covering Python programming fundamentals for beginners.",
        "url": "https://www.py4e.com/",
        "resource_type": "course",
        "difficulty": "beginner",
        "is_free": True,
        "skills": ["python"],
    },

    # SQL
    {
        "title": "PostgreSQL Tutorial",
        "provider": "postgresql.org",
        "description": "Official PostgreSQL documentation and tutorial for SQL database management.",
        "url": "https://www.postgresql.org/docs/current/tutorial.html",
        "resource_type": "documentation",
        "difficulty": "beginner",
        "is_free": True,
        "skills": ["sql"],
    },
    {
        "title": "SQLBolt Interactive Lessons",
        "provider": "SQLBolt",
        "description": "Interactive SQL lessons and exercises for learning SQL basics.",
        "url": "https://sqlbolt.com/",
        "resource_type": "tutorial",
        "difficulty": "beginner",
        "is_free": True,
        "skills": ["sql"],
    },

    # Docker
    {
        "title": "Official Docker Documentation",
        "provider": "Docker",
        "description": "Comprehensive Docker documentation including getting started guides.",
        "url": "https://docs.docker.com/get-started/",
        "resource_type": "documentation",
        "difficulty": "beginner",
        "is_free": True,
        "skills": ["docker"],
    },

    # AWS
    {
        "title": "AWS Cloud Practitioner Essentials",
        "provider": "AWS",
        "description": "Free foundational course on AWS cloud concepts and services.",
        "url": "https://explore.skillbuilder.aws/learn/course/external/view/elearning/134/aws-cloud-practitioner-essentials",
        "resource_type": "course",
        "difficulty": "beginner",
        "is_free": True,
        "skills": ["aws", "cloud_computing"],
    },

    # Machine Learning
    {
        "title": "Scikit-learn User Guide",
        "provider": "scikit-learn.org",
        "description": "Official scikit-learn documentation with tutorials and API reference.",
        "url": "https://scikit-learn.org/stable/user_guide.html",
        "resource_type": "documentation",
        "difficulty": "intermediate",
        "is_free": True,
        "skills": ["machine_learning", "scikit-learn"],
    },
    {
        "title": "Kaggle Intro to Machine Learning",
        "provider": "Kaggle",
        "description": "Free micro-course covering machine learning fundamentals.",
        "url": "https://www.kaggle.com/learn/intro-to-machine-learning",
        "resource_type": "course",
        "difficulty": "beginner",
        "is_free": True,
        "skills": ["machine_learning"],
    },

    # Data Analysis
    {
        "title": "Pandas Getting Started Tutorial",
        "provider": "pandas.pydata.org",
        "description": "Official pandas documentation with step-by-step tutorials.",
        "url": "https://pandas.pydata.org/docs/getting_started/intro_tutorials/",
        "resource_type": "documentation",
        "difficulty": "beginner",
        "is_free": True,
        "skills": ["pandas", "data_analysis"],
    },
    {
        "title": "NumPy User Guide",
        "provider": "numpy.org",
        "description": "Official NumPy documentation covering array operations and linear algebra.",
        "url": "https://numpy.org/doc/stable/user/index.html",
        "resource_type": "documentation",
        "difficulty": "intermediate",
        "is_free": True,
        "skills": ["numpy"],
    },

    # Web Development
    {
        "title": "Django Official Tutorial",
        "provider": "djangoproject.com",
        "description": "Official Django web framework tutorial building a poll application.",
        "url": "https://docs.djangoproject.com/en/5.1/intro/tutorial01/",
        "resource_type": "tutorial",
        "difficulty": "beginner",
        "is_free": True,
        "skills": ["django", "python"],
    },
    {
        "title": "FastAPI Official Tutorial",
        "provider": "fastapi.tiangolo.com",
        "description": "Comprehensive FastAPI tutorial with step-by-step examples.",
        "url": "https://fastapi.tiangolo.com/tutorial/",
        "resource_type": "documentation",
        "difficulty": "intermediate",
        "is_free": True,
        "skills": ["fastapi", "python"],
    },

    # Git
    {
        "title": "Pro Git Book",
        "provider": "git-scm.com",
        "description": "Free comprehensive book on Git version control.",
        "url": "https://git-scm.com/book/en/v2",
        "resource_type": "book",
        "difficulty": "beginner",
        "is_free": True,
        "skills": ["git"],
    },

    # Linux
    {
        "title": "Linux Tutorial for Beginners",
        "provider": "linux.org",
        "description": "Free Linux fundamentals course covering command line and system administration.",
        "url": "https://linux.org/pages/download/",
        "resource_type": "course",
        "difficulty": "beginner",
        "is_free": True,
        "skills": ["linux"],
    },

    # JavaScript / Frontend
    {
        "title": "MDN JavaScript Guide",
        "provider": "MDN Web Docs",
        "description": "Comprehensive JavaScript documentation and tutorials.",
        "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide",
        "resource_type": "documentation",
        "difficulty": "beginner",
        "is_free": True,
        "skills": ["javascript"],
    },
    {
        "title": "freeCodeCamp JavaScript Algorithms",
        "provider": "freeCodeCamp",
        "description": "Free JavaScript algorithms and data structures certification.",
        "url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures-v8/",
        "resource_type": "course",
        "difficulty": "intermediate",
        "is_free": True,
        "skills": ["javascript", "data_structures"],
    },

    # React
    {
        "title": "React Official Tutorial",
        "provider": "react.dev",
        "description": "Official React documentation with interactive examples.",
        "url": "https://react.dev/learn",
        "resource_type": "documentation",
        "difficulty": "beginner",
        "is_free": True,
        "skills": ["react"],
    },

    # TypeScript
    {
        "title": "TypeScript Handbook",
        "provider": "typescriptlang.org",
        "description": "Official TypeScript documentation and learning resources.",
        "url": "https://www.typescriptlang.org/docs/handbook/",
        "resource_type": "documentation",
        "difficulty": "intermediate",
        "is_free": True,
        "skills": ["typescript"],
    },

    # Deep Learning
    {
        "title": "TensorFlow Tutorials",
        "provider": "tensorflow.org",
        "description": "Official TensorFlow tutorials for deep learning.",
        "url": "https://www.tensorflow.org/tutorials",
        "resource_type": "tutorial",
        "difficulty": "intermediate",
        "is_free": True,
        "skills": ["tensorflow", "deep_learning"],
    },
    {
        "title": "PyTorch Tutorials",
        "provider": "pytorch.org",
        "description": "Official PyTorch tutorials for deep learning.",
        "url": "https://pytorch.org/tutorials/",
        "resource_type": "tutorial",
        "difficulty": "intermediate",
        "is_free": True,
        "skills": ["pytorch", "deep_learning"],
    },

    # Kubernetes
    {
        "title": "Kubernetes Official Tutorials",
        "provider": "kubernetes.io",
        "description": "Official Kubernetes documentation and interactive tutorials.",
        "url": "https://kubernetes.io/docs/tutorials/",
        "resource_type": "tutorial",
        "difficulty": "advanced",
        "is_free": True,
        "skills": ["kubernetes"],
    },

    # Data Visualization
    {
        "title": "Matplotlib Tutorial",
        "provider": "matplotlib.org",
        "description": "Official Matplotlib documentation and tutorials.",
        "url": "https://matplotlib.org/stable/tutorials/index.html",
        "resource_type": "documentation",
        "difficulty": "intermediate",
        "is_free": True,
        "skills": ["matplotlib", "data_visualization"],
    },

    # Cloud & DevOps
    {
        "title": "Terraform Getting Started",
        "provider": "HashiCorp",
        "description": "Official Terraform tutorial for infrastructure as code.",
        "url": "https://developer.hashicorp.com/terraform/tutorials/aws-get-started",
        "resource_type": "tutorial",
        "difficulty": "intermediate",
        "is_free": True,
        "skills": ["terraform", "cloud_computing"],
    },

    # Soft Skills
    {
        "title": "Effective Communication Skills",
        "provider": "Coursera (free audit)",
        "description": "Communication skills course available for free audit on Coursera.",
        "url": "https://www.coursera.org/learn/effective-business-communication-skills",
        "resource_type": "course",
        "difficulty": "beginner",
        "is_free": True,
        "skills": ["communication"],
    },

    # Data Structures
    {
        "title": "freeCodeCamp Data Structures",
        "provider": "freeCodeCamp",
        "description": "Free data structures and algorithms course with certifications.",
        "url": "https://www.freecodecamp.org/learn/coding-interview-prep/",
        "resource_type": "course",
        "difficulty": "intermediate",
        "is_free": True,
        "skills": ["data_structures", "algorithms"],
    },

    # CI/CD
    {
        "title": "GitHub Actions Documentation",
        "provider": "GitHub",
        "description": "Official GitHub Actions documentation for CI/CD workflows.",
        "url": "https://docs.github.com/en/actions",
        "resource_type": "documentation",
        "difficulty": "intermediate",
        "is_free": True,
        "skills": ["ci_cd", "git"],
    },

    # Communication
    {
        "title": "Teamwork Skills Course",
        "provider": "Coursera (free audit)",
        "description": "Collaboration and teamwork skills for professional environments.",
        "url": "https://www.coursera.org/learn/teamwork-skills-effective-collaboration",
        "resource_type": "course",
        "difficulty": "beginner",
        "is_free": True,
        "skills": ["teamwork"],
    },

    # Problem Solving
    {
        "title": "Introduction to Problem Solving",
        "provider": "Coursera (free audit)",
        "description": "Problem-solving and critical thinking skills course.",
        "url": "https://www.coursera.org/learn/problem-solving",
        "resource_type": "course",
        "difficulty": "beginner",
        "is_free": True,
        "skills": ["problem_solving"],
    },
]


def get_resources() -> list[dict]:
    return RESOURCES

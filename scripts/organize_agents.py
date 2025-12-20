import os
import shutil

BASE_DIR = "codeswarm/agents/armada"
CATEGORIES = {
    "backend": ["api", "backend", "django", "rails", "flask", "fastapi", "spring", "dotnet", "java", "python", "ruby", "php", "golang", "csharp", "cpp", "rust", "scala", "node", "express", "graphql"],
    "frontend": ["frontend", "react", "vue", "angular", "ios", "android", "mobile", "flutter", "swift", "kotlin", "typescript", "javascript", "tailwind", "ui", "ux", "css", "html"],
    "ops": ["devops", "cloud", "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "sre", "platform", "infrastructure", "ci", "cd", "build", "deployment", "linux", "bash", "shell"],
    "data": ["data", "sql", "postgres", "mysql", "database", "analytics", "ml", "ai", "machine_learning", "nlp", "vision", "pandas", "numpy", "jupyter"],
    "security": ["security", "penetration", "auditor", "compliance", "risk"],
    "product": ["product", "project", "agile", "scrum", "business", "marketing", "content", "copywriter", "seo", "growth", "sales"],
    "qa": ["qa_expert", "tester", "test", "quality"],
    "docs": ["docs", "documentation", "writer", "markdown"],
}

def organize_agents():
    # Create category directories
    for category in CATEGORIES:
        os.makedirs(os.path.join(BASE_DIR, category), exist_ok=True)
    
    # Also create a 'general' category for everything else
    os.makedirs(os.path.join(BASE_DIR, "general"), exist_ok=True)

    # List all files
    files = [f for f in os.listdir(BASE_DIR) if os.path.isfile(os.path.join(BASE_DIR, f))]
    
    for filename in files:
        if filename == "__init__.py":
            continue
            
        # Determine category
        target_category = "general"
        lower_name = filename.lower()
        
        for category, keywords in CATEGORIES.items():
            if any(k in lower_name for k in keywords):
                target_category = category
                break
        
        # Move file
        src = os.path.join(BASE_DIR, filename)
        dst = os.path.join(BASE_DIR, target_category, filename)
        
        print(f"Moving {filename} -> {target_category}/")
        shutil.move(src, dst)

if __name__ == "__main__":
    organize_agents()

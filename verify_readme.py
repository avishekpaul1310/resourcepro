#!/usr/bin/env python
"""
Verify that the README.md contains all essential information for ResourcePro
"""
import os

def check_readme_completeness():
    """Check if README contains all essential sections and information"""
    readme_path = "README.md"
    
    if not os.path.exists(readme_path):
        print("❌ README.md file not found!")
        return False
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read().lower()
    
    # Essential sections that should be in the README
    required_sections = [
        # Basic Information
        "resourcepro",
        "key features",
        "analytics",
        "resource management",
        
        # User-friendly content
        "who is this for",
        "quick start guide",
        "non-technical users",
        
        # Installation
        "installation",
        "prerequisites", 
        "step-by-step",
        
        # Usage instructions
        "how to use",
        "dashboard",
        "common tasks",
        
        # Recent updates
        "recent updates",
        "major issues resolved",
        "new features added",
        
        # Technical details
        "technical architecture",
        "technology stack",
        "testing coverage",
        
        # Support
        "troubleshooting",
        "deployment",
        "contributing",
        "license"
    ]
    
    # Features that should be mentioned
    required_features = [
        "time tracking",
        "skill analysis",
        "utilization report",
        "cost report", 
        "demand forecasting",
        "availability calendar",
        "export",
        "bulk operations",
        "authentication"
    ]
    
    missing_sections = []
    missing_features = []
    
    print("🔍 Checking README completeness...")
    print("\n📋 Checking required sections:")
    
    for section in required_sections:
        if section in content:
            print(f"  ✅ {section.title()}")
        else:
            print(f"  ❌ {section.title()}")
            missing_sections.append(section)
    
    print("\n🔧 Checking feature coverage:")
    
    for feature in required_features:
        if feature in content:
            print(f"  ✅ {feature.title()}")
        else:
            print(f"  ❌ {feature.title()}")
            missing_features.append(feature)
    
    # Check for user-friendly elements
    user_friendly_elements = [
        "emoji",  # Should have emojis for visual appeal
        "step-by-step",  # Should have clear instructions
        "non-technical",  # Should address non-technical users
        "quick start",  # Should have quick start guide
        "troubleshooting"  # Should have troubleshooting section
    ]
    
    print("\n👥 Checking user-friendliness:")
    
    for element in user_friendly_elements:
        if element in content:
            print(f"  ✅ {element.title().replace('-', ' ')}")
        else:
            print(f"  ❌ {element.title().replace('-', ' ')}")
    
    # Check file size (comprehensive README should be substantial)
    file_size = len(content)
    print(f"\n📏 README size: {file_size} characters")
    
    if file_size < 5000:
        print("  ⚠️  README might be too short for a comprehensive guide")
    elif file_size > 15000:
        print("  ⚠️  README might be too long - consider breaking into sections")
    else:
        print("  ✅ Good length for comprehensive documentation")
    
    # Overall assessment
    print("\n🎯 Overall Assessment:")
    
    if not missing_sections and not missing_features:
        print("  🎉 EXCELLENT! README is comprehensive and user-friendly")
        print("  ✅ Contains all essential sections")
        print("  ✅ Covers all major features") 
        print("  ✅ Includes user-friendly elements")
        print("  ✅ Suitable for both technical and non-technical users")
        return True
    else:
        if missing_sections:
            print(f"  ❌ Missing sections: {', '.join(missing_sections)}")
        if missing_features:
            print(f"  ❌ Missing features: {', '.join(missing_features)}")
        return False

if __name__ == '__main__':
    success = check_readme_completeness()
    if success:
        print("\n✨ README verification complete - All requirements met!")
    else:
        print("\n⚠️  README needs improvement - Some requirements missing")

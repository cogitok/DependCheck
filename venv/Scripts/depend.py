import os
import subprocess
import xml.etree.ElementTree as ET
import re

# location of the text files containing the repository list, old dependencies, and new dependencies
repo_list_file = 'repo_list.txt'
old_deps_file = 'old_deps.txt'
new_deps_file = 'new_deps.txt'

# read the list of repositories from the text file
with open(repo_list_file, 'r') as file:
    repo_list = file.readlines()

# read the list of old dependencies from the text file
with open(old_deps_file, 'r') as file:
    old_deps = file.readlines()

# read the list of new dependencies from the text file
with open(new_deps_file, 'r') as file:
    new_deps = file.readlines()

# iterate over each repository in the list
for repo in repo_list:
    repo = repo.strip()
    print(f'Processing repository {repo}...')

    # navigate to the repository directory
    os.chdir(repo)

    # run mvn dependency:tree to get the list of dependencies
    process = subprocess.run(['C:\\opt\\apache-maven-3.8.1\\bin\\mvn.cmd', 'dependency:tree'], capture_output=True, text=True)
    dependencies = process.stdout
    print(dependencies)

    # Check for dependencies from spring-boot-session
    dependencies = process.stdout.split('\n')
    for dependency in dependencies:
        match = re.search("(.*org\.springframework\.session.*)",dependency)
        if match:
            dependency_line = match.group(1)
            artifact_id = dependency.split(':')[1]
            version = dependency.split(':')[2]
            print(f'Found old dependency: {artifact_id}:{version}')
            print('Will Remove those Dependencies now...')
            # Remove the dependency from the POM file
            os.system(f'mvn dependency:purge-local-repository -DactTransitively={artifact_id} -Dverbose')
            print('SUCCESS PURGED')

            # Remove the dependency from the pom.xml
            tree = ET.parse("pom.xml")
            root = tree.getroot()
            for dependency in root.iter("dependency"):
                if dependency.find("artifactId").text == artifact_id:
                    root.remove(dependency)
                    tree.write("pom.xml")
                    print('REMOVED FROM POM', dependency)
                    break
    # Verify that the old dependencies are removed from the pom.xml
    tree = ET.parse("pom.xml")
    root = tree.getroot()
    for dependency in root.iter("dependency"):
        if dependency.find("artifactId").text.startswith("org.springframework.session"):
            print(f'Error: {dependency.find("artifactId").text}:{dependency.find("version").text} still exists in pom.xml')
            exit()


    # Re-run the build

    print('RUNNING MVN CLEAN INSTALL NOW')
    os.system('mvn clean install')

    print("BUILD WAS A SUCCESS!")
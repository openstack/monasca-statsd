
desc "Run tests"
task :test do
  sh "nosetests"
end

task :default => :test

task :release => :test do
  sh "python setup.py sdist upload"
end

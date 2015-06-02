#
# Cookbook Name:: web_application
# Recipe:: database
#
# Copyright (c) 2015 The Authors, All Rights Reserved.

# Configure the mysql2 Ruby gem.
mysql2_chef_gem 'default' do
  action :install
end

# Configure the MySQL client.
mysql_client 'default' do
  action :create
end

# Configure the MySQL service.
mysql_service 'default' do
  initial_root_password node['mysql']['server_root_password']
  action [:create, :start]
end

# Create the database instance.
mysql_database node['web_application']['database']['dbname'] do
  connection(
    :host => node['web_application']['database']['host'],
    :username => node['web_application']['database']['username'],
    :password => node['web_application']['database']['password']
  )
  action :create
end

# Add a database user.
mysql_database_user node['web_application']['database']['app']['username'] do
  connection(
    :host => node['web_application']['database']['host'],
    :username => node['web_application']['database']['username'],
    :password => node['web_application']['database']['password']
  )
  password node['web_application']['database']['app']['password']
  database_name node['web_application']['database']['dbname']
  host node['web_application']['database']['host']
  action [:create, :grant]
end

# Write schema seed file to filesystem.
cookbook_file node['web_application']['database']['seed_file'] do
  source 'create-tables.sql'
  owner 'root'
  group 'root'
  mode '0600'
end

# Seed the database with a table and test data.
execute 'initialize database' do
  command "mysql -h #{node['web_application']['database']['host']} -u #{node['web_application']['database']['app']['username']} -p#{node['web_application']['database']['app']['password']} -D #{node['web_application']['database']['dbname']} < #{node['web_application']['database']['seed_file']}"
  not_if  "mysql -h #{node['web_application']['database']['host']} -u #{node['web_application']['database']['app']['username']} -p#{node['web_application']['database']['app']['password']} -D #{node['web_application']['database']['dbname']} -e 'describe customers;'"
end

#
# Cookbook Name:: web_application
# Recipe:: webserver
#
# Copyright (c) 2015 The Authors, All Rights Reserved.

# Install Apache and configure its service.
include_recipe 'apache2::default'

# Create and enable our custom site.
web_app 'customers' do
  template 'customers.conf.erb'
end

# Create the document root.
directory '/srv/apache/customers/' do
  recursive true
end

# Write a default home page.
template "#{node['apache']['docroot_dir']}/index.php" do
  source 'index.php.erb'
  mode '0644'
  owner node['web_application']['user']
  group node['web_application']['group']
end

# Open port 80 to incoming traffic.
include_recipe 'iptables'
iptables_rule 'firewall_http'

# Install the mod_php5 Apache module.
include_recipe 'apache2::mod_php5'

# Install php-mysql.
package 'php-mysql' do
  action :install
  notifies :restart, 'service[apache2]'
end

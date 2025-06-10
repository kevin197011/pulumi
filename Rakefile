# Copyright (c) 2025 Kk
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

require 'time'

task default: %w[push]

task :push do
  system 'git add .'
  system "git commit -m 'Update #{Time.now}.'"
  system 'git pull'
  system 'git push origin main'
end

task :fmt do
  system 'black .'
  system 'isort .'
  system 'ruff check .'
  system 'ruff format .'
end

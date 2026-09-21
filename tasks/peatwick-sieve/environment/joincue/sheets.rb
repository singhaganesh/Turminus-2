# frozen_string_literal: true

module Sheets
  DIR = '/app/lutcards'

  module_function

  def load
    maps = {}
    Dir.glob(File.join(DIR, '*.map')).sort.each do |path|
      rel = nil
      names = []
      File.readlines(path, chomp: true).each do |line|
        if line.start_with?('REL ')
          rel = line.split(' ', 2)[1]
        elsif line.start_with?('ASSAY ')
          names << line.split(' ', 2)[1]
        end
      end
      maps[rel] = names if rel
    end
    maps
  end
end

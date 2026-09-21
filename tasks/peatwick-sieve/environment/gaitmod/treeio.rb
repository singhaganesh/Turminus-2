# frozen_string_literal: true

require 'digest'
require 'find'

module Treeio
  module_function

  def files(root)
    out = []
    return out unless Dir.exist?(root)

    Find.find(root) do |p|
      next unless File.file?(p)

      rel = p.sub(%r{\A#{Regexp.escape(root)}/?}, '')
      next if rel.empty? || rel.start_with?('.')

      out << rel
    end
    out.sort
  end

  def digest(path)
    Digest::SHA256.file(path).hexdigest
  end
end

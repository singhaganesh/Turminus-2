# frozen_string_literal: true

require 'digest'
require 'find'

module Dust
  FOLD = '/app/livefold'
  SNAP = '/app/snapurn/seals'

  module_function

  def newest_root
    File.join(SNAP, Dir.children(SNAP).sort.last)
  end

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

  def note
    File.read('/app/opside/SEAL_FIRST.txt')
  end

  def dirty?
    b = newest_root
    (files(FOLD) | files(b)).any? do |rel|
      pd = File.join(FOLD, rel)
      pb = File.join(b, rel)
      if File.file?(pd) && File.file?(pb)
        Digest::SHA256.file(pd).hexdigest != Digest::SHA256.file(pb).hexdigest
      else
        File.file?(pd) || File.file?(pb)
      end
    end
  end
end

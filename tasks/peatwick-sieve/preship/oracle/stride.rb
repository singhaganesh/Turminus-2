# frozen_string_literal: true

require_relative 'treeio'

module Walkbay
  FOLD = '/app/livefold'
  SNAP = '/app/snapurn/seals'
  SCRATCH = '/app/inkvat/delta.lst'

  module_function

  def newest
    Dir.children(SNAP).sort.last
  end

  def prior
    kids = Dir.children(SNAP).sort
    kids.length >= 2 ? kids[-2] : kids[-1]
  end

  def loom
    b = File.join(SNAP, newest)
    changed = []
    (Treeio.files(FOLD) | Treeio.files(b)).each do |rel|
      pd = File.join(FOLD, rel)
      pb = File.join(b, rel)
      if File.file?(pd) && File.file?(pb)
        next if Treeio.digest(pd) == Treeio.digest(pb)

        changed << rel
      elsif File.file?(pd) || File.file?(pb)
        changed << rel
      end
    end
    body = changed.map { |r| "live:#{r}" }.join("\n")
    body += "\n" unless body.empty?
    File.write(SCRATCH, body)
    changed
  end
end

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
    a = File.join(SNAP, prior)
    b = File.join(SNAP, newest)
    changed = []
    (Treeio.files(a) | Treeio.files(b)).each do |rel|
      pa = File.join(a, rel)
      pb = File.join(b, rel)
      same = File.file?(pa) && File.file?(pb) && Treeio.digest(pa) == Treeio.digest(pb)
      next if same

      changed << rel if File.file?(pa) || File.file?(pb)
    end
    File.write(SCRATCH, changed.map { |r| "seal:#{r}" }.join("\n"))
    File.write(SCRATCH, File.read(SCRATCH) + "\n") unless changed.empty?
    changed
  end
end

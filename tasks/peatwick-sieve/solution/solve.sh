#!/bin/bash
set -euo pipefail

cat > /app/gaitmod/stride.rb << 'END_STRIDE'
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
END_STRIDE

cat > /app/joincue/latch.rb << 'END_LATCH'
# frozen_string_literal: true

require 'json'
require_relative 'sheets'

module Bindpit
  SCRATCH = '/app/inkvat/delta.lst'
  ROSTER = '/app/inkvat/pick.json'
  LEDGER = '/app/inkvat/sieve.bin'

  module_function

  def put16(buf, n)
    buf << [n].pack('n')
  end

  def hitch
    raw = File.exist?(SCRATCH) ? File.read(SCRATCH) : ''
    tokens = raw.split
    maps = Sheets.load
    rows = []
    tokens.each do |tok|
      next if tok.nil? || tok.empty?

      rel = tok.sub(/\A(live|seal):/, '')
      rel = rel.sub(%r{\A/+}, '')
      next if rel.empty?

      assays = (maps[rel] || []).uniq.sort
      next if assays.empty?

      rows << { 'path' => "live:#{rel}", 'assays' => assays }
    end
    rows.sort_by! { |r| r['path'] }
    File.write(ROSTER, JSON.pretty_generate({ 'rows' => rows }) + "\n")
    buf = +''.b
    rows.each do |r|
      pb = r['path'].encode('UTF-8')
      put16(buf, pb.bytesize)
      buf << pb
      put16(buf, r['assays'].length)
      r['assays'].each do |a|
        ab = a.encode('UTF-8')
        put16(buf, ab.bytesize)
        buf << ab
      end
    end
    File.binwrite(LEDGER, buf)
    rows
  end
end
END_LATCH

cat > /app/stillbay/vale.rb << 'END_VALE'
# frozen_string_literal: true

require 'json'
require_relative 'dust'

module Hushgate
  ROSTER = '/app/inkvat/pick.json'

  module_function

  def vale
    Dust.note
    rows = JSON.parse(File.read(ROSTER))['rows'] || []
    return 1 if Dust.dirty? && rows.empty?

    0
  end
end
END_VALE

bash /app/knit.sh
/app/bin/peatwick kindle

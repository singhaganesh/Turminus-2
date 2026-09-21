# frozen_string_literal: true

require 'json'
require_relative 'sheets'

module Bindpit
  SCRATCH = '/app/inkvat/delta.lst'
  ROSTER = '/app/inkvat/pick.json'
  LEDGER = '/app/inkvat/sieve.bin'

  module_function

  def hitch
    raw = File.exist?(SCRATCH) ? File.read(SCRATCH) : ''
    tokens = raw.split
    maps = Sheets.load
    rows = []
    tokens.each do |tok|
      rel = tok.sub(/\A(live|seal):/, '')
      key = File.basename(rel)
      assays = []
      maps.each do |mrel, names|
        assays.concat(names) if File.basename(mrel) == key
      end
      assays = assays.uniq.sort
      next if assays.empty?

      rows << { 'path' => "live:#{rel}", 'assays' => assays }
    end
    File.write(ROSTER, JSON.pretty_generate({ 'rows' => rows }) + "\n")
    buf = +''.b
    rows.each do |r|
      pb = r['path'].encode('UTF-8')
      buf << [pb.bytesize].pack('n') << pb
      buf << [r['assays'].length].pack('n')
      r['assays'].each do |a|
        ab = a.encode('UTF-8')
        buf << [ab.bytesize].pack('n') << ab
      end
    end
    File.binwrite(LEDGER, buf)
    rows
  end
end

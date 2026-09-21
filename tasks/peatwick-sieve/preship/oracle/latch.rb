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

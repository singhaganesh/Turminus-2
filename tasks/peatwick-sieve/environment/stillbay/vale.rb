# frozen_string_literal: true

require 'json'
require_relative 'dust'

module Hushgate
  ROSTER = '/app/inkvat/pick.json'
  SCRATCH = '/app/inkvat/delta.lst'

  module_function

  def vale
    Dust.note
    rows = JSON.parse(File.read(ROSTER))['rows'] || []
    scratch = File.exist?(SCRATCH) ? File.read(SCRATCH) : ''
    return 1 if scratch.strip.empty? && rows.empty?

    0
  end
end

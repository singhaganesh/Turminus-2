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

# frozen_string_literal: true

# Lists consecutive snapshot names for ops notes. Not on the mill path.
module Pairhint
  def self.names
    Dir.children('/app/snapurn/seals').sort
  end
end

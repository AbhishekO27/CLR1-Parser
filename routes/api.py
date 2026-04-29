from flask import Blueprint, request, jsonify
from parser.grammar import parse_grammar_text, get_terminals
from parser.first import compute_first
from parser.engine import parse

api = Blueprint("api", __name__)

@api.route("/parse", methods=["POST"])
def api_parse():
    data = request.json

    grammar = parse_grammar_text(data["grammar"])
    terminals = get_terminals(grammar)
    first = compute_first(grammar, terminals)

    # call LR1 builder modules...

    return jsonify({...})
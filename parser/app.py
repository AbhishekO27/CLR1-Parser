from flask import Flask, request, jsonify
from grammar import parse_grammar_text, get_terminals
from firs import compute_first
from states import build_canonical_collection
from table import build_parsing_table
from parser_engine import parse
from serialize import serialise_states, serialise_table

app = Flask(__name__)
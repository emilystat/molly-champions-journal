import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from dictionary_source import plain,extract,args_of,target_of
class DictionarySourceTests(unittest.TestCase):
 def test_nested_links_keep_template_argument_together(self):
  self.assertEqual(plain('{{non-gloss|A [[small|tiny]] [[bird]].}}'),'A tiny bird.')
 def test_form_templates_retain_base_word(self):
  self.assertEqual(target_of('en-superlative of|bland'),'bland')
  self.assertEqual(plain('{{en-superlative of|bland}}'),'Superlative of bland')
 def test_nested_senses_match_source_context(self):
  raw='==English==\n===Noun===\n# {{non-gloss|Senses relating to size.}}\n## A decrease in size or length.\n## An agreement to marry.\n'
  result=extract(raw,{'word':'contraction','pos':['noun'],'_context':'a decrease in length'})
  self.assertEqual(result[0]['text'],'A decrease in size or length.')
  self.assertFalse(any(g['text'].startswith('Senses relating') for g in result))
 def test_unsafe_and_unsupported_text_is_not_silently_accepted(self):
  self.assertEqual(plain('{{unknown-template|en|guess}}'),'')
  raw='==English==\n===Noun===\n# {{lb|en|vulgar}} A rude meaning.\n# A calm meaning.\n'
  self.assertEqual(extract(raw,{'pos':['noun']})[0]['text'],'A calm meaning.')
 def test_foreign_section_is_not_presented_as_english(self):
  self.assertEqual(extract('==Italian==\n===Noun===\n# A village.\n',{'pos':['noun']}),[])
if __name__=='__main__':unittest.main()

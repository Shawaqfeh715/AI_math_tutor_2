import re
import spacy
from functools import lru_cache
from src.backend.classifier import MathClassifier
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %'
                           '(levelname)s - %(message)s')
logger=logging.getLogger(__name__)

nlp=spacy.load("en_core_web_sm",disable=[
    'ner','parser'])


def tokenize(text:str)->list:
    doc=nlp(text)
    tokens=[token.text for token in doc if token.text.strip()]
    logger.debug(f'Tokens: {tokens}')
    return tokens


class MathNLPProcessor:
      def __init__(self):
          self.classifier=MathClassifier()
          self.math_symbols={'x':"*",
                             "÷":"/","-":"-",
                             "²":"^2",'π':"pi"}
          self.context=[]
          self.max_context=3
      @lru_cache(maxsize=128)
      def normalize_text(self,text:str)->str:
          text=text.lower().strip()
          for symbol,replacement in self.math_symbols.items():
              text=text.replace(symbol,replacement)
          text=re.sub(r'\s+',' ',text)
          logger.debug(f'Normalized:{text}')
          return text

      @staticmethod
      def remove_stopwords(tokens:list)->list:
          math_relevant={'x','y','z',
                         '=','+','-','*','/'
                         ,'pi','sin','cos','tan',
                         'derivative','area','circle','radius'}
          return [token for token in tokens
                  if token in math_relevant or token.isdigit()]

      @staticmethod
      def pos_tag(text:str)->list:
          doc=nlp(text)
          return [(token.text,token.pos_)
                  for token in doc if token.text in
                  {'x','y','z','=','+','-',
                   '*','/','pi','sin','cos','tan'} or token.pos_
                  in ["NOUN","NUM","SYM"]]
      def lexical_analysis(self,text:str)->dict:
          normalized=self.normalize_text(text)
          tokens= tokenize(normalized)
          tokens_no_stopwords=self.remove_stopwords(tokens)
          pos_tags=self.pos_tag(normalized)
          return {
                 "normalized":normalized,
                 "tokens":tokens,
                  "tokens_no_stopwords":
                  tokens_no_stopwords,
                  "pos_tags": pos_tags
          }
      @staticmethod
      def syntactic_analysis(text:str)->dict:
          doc=nlp(text)
          math_components=[token.text for
                           token in doc if token.pos_ in
                           ['NOUN','NUM','SYM'] or token.text in
                           {'x','y','z',"=","+","-",
                            "*","/","pi","sin","cos","tan"}]
          logger.debug(f'Math components:{math_components}')
          return {"math_components":math_components}

      @lru_cache(maxsize=64)
      def semantic_analysis(self,text:str,
                            syntactic_result:dict)->dict:
          classification=self.classifier.classify(text)
          math_expr=" ".join(syntactic_result
                             ["math_components"])
          try:
              from sympy import parse_expr
              parsed_expr=parse_expr(math_expr,transformations=('all',)
                                     ,evaluate=False)
              logger.info(f"Parsed expression:{parsed_expr}")
              return {
                  "classification":
                   classification.to_dict(),
                  "parsed_expression":str(parsed_expr),
                   "is_valid":True
              }
          except Exception as e:
                logger.error(f'Semantic analysis error:'
                             f'{str(e)}')
                return {
                     "classification":
                      classification.to_dict(),
                     "parsed_expression":
                    math_expr,
                    "is_valid":False,
                    "error":str(e)
                }
      @staticmethod
      def pragmatic_analysis(text:str,
                             classification:dict)->dict:
          intent="solve"
          if any(word in text.lower() for
                 word in ["explain","how","why"]):
              intent="explain"
          logger.debug(f'Intent detected:'
                       f'{intent}')
          return {'intent':intent,
                  "problem_type":classification['problem_type']}

      def discourse_integration(self,text:str
                                ,semantic_result:dict)->dict:
          self.context.append({"text":text,
                               "semantic_result":semantic_result})
          if len(self.context)>self.max_context:
              self.context.pop(0)
          logger.debug(f'Context updated:'
                       f'{len(self.context)} entries')
          return  {
                   "context": [item["text"]for item in self.context],
              "current_expression":
              semantic_result["parsed_expression"]
          }

      def process(self,text:str)->dict:
          try:
              lexical_result=self.lexical_analysis(text)
              syntactic_result=self.syntactic_analysis(lexical_result['normalized'])
              semantic_result=self.semantic_analysis(
                  lexical_result["normalized"],
                  syntactic_result
              )
              pragmatic_result=self.pragmatic_analysis(
                  lexical_result['normalized'],
                  semantic_result['classification'])
              discourse_result=self.discourse_integration(lexical_result['normalized'],
                                                          semantic_result)
              logger.info(f"Successfully processed input: {text}")
              return {
                  'lexical':lexical_result,
                   'syntactic':syntactic_result,
                   'semantic':semantic_result,
                   'pragmatic':pragmatic_result,
                   'discourse':discourse_result
              }
          except Exception as e:
                logger.error(f'NLP processing failed:'
                             f'{str(e)}')
                return {"error":str(e)}

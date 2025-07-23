import os
import gc
import time
import sys
from llama_cpp import Llama
from dotenv import load_dotenv
from src.llm.prompt import build_prompt, build_summary_prompt

load_dotenv()

MAX_TOKENS = 2048

llm = None
warmed_up = False

def load_model():
  global llm
  if llm == None:
    print("Loading LLM model...")
    llm = Llama(
      model_path = os.environ.get("MODEL_PATH"),
      n_gpu_layers=-1,
      n_ctx=MAX_TOKENS,
      n_threads=6,
    )

    print("LLM model loaded")
  return llm

def generate(prompt, max_tokens=None):
  load_model()
  llm_response = llm(
    prompt=prompt,
    max_tokens=max_tokens,
    stop=["Q:", "\n"],
    echo=True,
  )
  response_text = llm_response["choices"][0]["text"]
  assistant_response = extract_assistant_response(response_text)

  return assistant_response

def extract_assistant_response(response_text):
  marker = "<|start_header_id|>assistant<|end_header_id|>\n"
  _, _, rest = response_text.partition(marker)
  return rest.strip()

def warm_up():
  global warmed_up
  if warmed_up == True:
    return
  generate("Ping")
  warmed_up = True

def count_tokens(prompt):
  load_model()
  tokens = llm.tokenize(prompt.encode("utf-8"))
  return len(tokens)

def unload_model():
  global llm
  del llm
  gc.collect()

if __name__ == "__main__":
  cliOptions = {
    "--query": True,
    "--token": True,
  }

  if len(sys.argv) < 2 or sys.argv[1] not in cliOptions:
    print("Invalid argument. You must provide '--query' or '--token'.")
    exit(1)

  cliOption = sys.argv[1]

  t1 = time.time_ns() // 1_000_000
  load_model()
  t2 = time.time_ns() // 1_000_000
  model_time = t2-t1
  print(f"Model loaded in {model_time} ms.")
  print("Warming up model")
  t3 = time.time_ns() // 1_000_000
  generate("Ping")
  t4 = time.time_ns() // 1_000_000
  warmup_time = t4-t3
  print(f"Model warmed up in {warmup_time} ms.")

  if cliOption == "--query":
    print("Querying model...")
    t5 = time.time_ns() // 1_000_000
    context = """
  Exoplanet Detection Methods 10 527
  Hatzes et al. (2006) combined literature data with subsequent iodine observations from
  McDonaldObservatoryandTautenburgObservatorytoshowthattheRVvariationscontinued
  coherentlyinto2006andthattheCaiiHandKlinesshowednocoincidentvariation.Theycon-
  cludedthatthevariationsin βGemwerelikelyduetoaminimummass3M Jup companionwith
  period590d.
  4.3.5 Mayor and Queloz and 51 Pegasi b
  The first unambiguous detection of a planet-mass object orbiting a normal star was by Mayor
  and Queloz (1995) of Geneva Observatory. Mayor and Queloz used the ELODIE spectro-
  graph,whichachieved13m/sprecisionthroughoutstandingmechanicalstability.ELODIE(the
  successor to CORAVEL) was a fiber-fed spectrograph within a stable, temperature-controlled
  environment (Queloz et

  This paper reviews five different methods to detect exoplanets, including direct imaging,
  astrometry, radial velocity, transit event observation, and microlensing. These approaches could
  expand the sample size of exoplanets and further our understanding of the types, formation and
  evolution of exoplanets.
  1. Introduction
  Whether there are other Earth-like planets with life in the uni verse or whether there are exoplanets has
  always been attracting the attention of researchers. It was not until 1995 that a paper published by Mayor
  & Queloz in Nature changed people’s imagination of exoplanets, and researchers di scovered a planet
  with a minimum mass of 51% of the mass of Jupiter through long- term measurement of the radial
  velocity of the sun-like star 51 Peg [1]. This discovery has started the prelude to the study of extrasolar
  planets. In addition, as early as 1992, Wolszczan and Frail det ected three planetary companion objects

  Exoplanet Detection Methods 10 491
  Abstract: This chapter reviewsvarious methodsof detecting planetary companions to stars
  from an observational perspective, focusing on radial velocities, astrometry, direct imaging,
  transits, and gravitational microlensing. For each method, this chapter first derives or sum-
  marizes the basic observable phenomena that are used to infer the existence of planetary
  companions aswell as the physical properties of the planets and hoststars that can be derived
  from the measurement of these signals. This chapter then outlines the general experimental
  requirementstorobustly detectthe signalsusing eachmethod,bycomparing theirmagnitude
  tothetypicalsourcesofmeasurementuncertainty.Thischaptergoesontocomparethevarious
  methodsto each other by outlining the regions of planet and host star parameterspace where
  each method is most sensitive, stressing the complementarity of the ensemble of the methods
  at our disposal. Finally, there is a brief reviewof the history of the young exoplanet field, from
  the

  Exoplanet Detection Methods 10 531
  The astrometric detection of planets discovered by other means has produced substan-
  tially more results, primarily because the approximate astrometric signals are known from
  prior radial velocity work, and so searches are more efficient. Most fruitful has been work
  on nearby stars employing theHubble Space TelescopeFine Guidance Sensor, which is capa-
  ble of precise astrometry of bright stars. This has revealed some high-mass planet candidates
  from radial velocity surveys to be binary stars in face-on orbits and has revealed the mutual
  inclinations of planets in multiplanet systems (Bean et al.2007;B e a na n dS e i f a h r t2009;
  McArthur et al.2010).
  5.2 Imaging
  5.2.1 2M1207 b
  Chauvin et al. (2010)describetheir surveyof young, nearby stars for low mass,possibly plan-
  etary companions using the ESO/VLT 8m
  """
    prompt = build_prompt(
      question="What is the easiest way to detect an exoplanet as an amateur astronomer?",
      context=context,
      summary=None,
      conversation=None,
    )
    response = generate(prompt)
    t6 = time.time_ns() // 1_000_000
    query_time = t6-t5
    print(f"Query processed in {query_time} ms.")
    print("Response:")
    print(str(response))
  elif cliOption == "--token":
    prompt = build_summary_prompt("")
    t7 = time.time_ns() // 1_000_000
    tokens = count_tokens(prompt)
    t8 = time.time_ns() // 1_000_000
    token_time = t8-t7
    print(f"Tokens processed in {token_time} ms.")
    print(f"Total tokens: {tokens}")

from typing import Optional
import uvicorn

from fastapi import FastAPI, Body, Depends, HTTPException,  File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from config import *
from pydantic import BaseModel
import json

# import data
from hotaSolana.hotaSolanaDataBase import *
from hotaSolana.hotaSolanaData import *
from hotaSolana.bs58 import bs58

from baseAPI import *

app = FastAPI(title="Solana API",
              description="Solana API Management",
              version="v2.0",
              contact={
                  "name": "Hotamago Master",
                  "url": "https://www.linkedin.com/in/hotamago/",
              })

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Solana Client
client = HotaSolanaRPC(programId, False, "devnet")

# Solana instruction data
@BaseInstructionDataClass(name="init_voter")
class VoterInitInstruction:
    cccd_sha256=HotaHex(32)

@BaseInstructionDataClass(name="init_candidate")
class CandidateInitInstruction:
    pass

@BaseInstructionDataClass(name="vote")
class VoteInstruction():
    pass

# Account data
@BaseStructClass
class VoterData:
    owner=HotaPublicKey()
    cccd_sha256=HotaHex(32)
    vote_who=HotaPublicKey()
    voted=HotaUint8(0)

@BaseStructClass
class CandidateData:
    owner=HotaPublicKey()
    num_votes=HotaUint64(0)


# Router
class InitVoterModel(BaseModel):
    private_key: str
    cccd: str

@app.post("/init-voter")
async def init_voter(data: InitVoterModel):
    def tryfcn():
        owner_keypair = makeKeyPair(data.private_key)
        cccd_sha256 = hash256(data.cccd).hex()

        voterInitInstruction = VoterInitInstruction()
        voterInitInstruction.get("cccd_sha256").object2struct(cccd_sha256)

        voterPublicKey = findProgramAddress(
                createBytesFromArrayBytes(
                    owner_keypair.public_key.byte_value,
                    "voter".encode("utf-8"),
                ),
                client.program_id
            )
        
        transaction_address = client.send_transaction(
            voterInitInstruction,
            [
                makeKeyPair(payerPrivateKey).public_key,
                owner_keypair.public_key,
                voterPublicKey,
                makePublicKey(sysvar_rent),
                makePublicKey(system_program),
            ],
            [
                makeKeyPair(payerPrivateKey),
                owner_keypair
            ]
        )

        return {
            "transaction_address": transaction_address,
            "public_key": bs58.encode(voterPublicKey.byte_value),
        }

    return make_response_auto_catch(tryfcn)

class InitCandidateModel(BaseModel):
    private_key: str

@app.post("/init-candidate")
async def init_candidate(secretKey: str):
    def tryfcn():
        owner_keypair = makeKeyPair(secretKey)
        candidatePublicKey = findProgramAddress(
                createBytesFromArrayBytes(
                    owner_keypair.public_key.byte_value,
                    "candidate".encode("utf-8"),
                ),
                client.program_id
            )

        transaction_address = client.send_transaction(
            CandidateInitInstruction(),
            [
                makeKeyPair(payerPrivateKey).public_key,
                owner_keypair.public_key,
                candidatePublicKey,
                makePublicKey(sysvar_rent),
                makePublicKey(system_program),
            ],
            [
                makeKeyPair(payerPrivateKey),
                owner_keypair
            ]
        )

        return {
            "transaction_address": transaction_address,
            "public_key": bs58.encode(candidatePublicKey.byte_value),
        }
    
    return make_response_auto_catch(tryfcn)

class VoteModel(BaseModel):
    owner_private_key: str
    candidate_public_Key: str
@app.post("/send-vote")
async def send_vote(data: VoteModel):
    def tryfcn():
        owner_keypair = makeKeyPair(data.owner_private_key)
        voter_public_key = findProgramAddress(
                createBytesFromArrayBytes(
                    owner_keypair.public_key.byte_value,
                    "voter".encode("utf-8"),
                ),
                client.program_id
            )
        candidate_public_Key = makePublicKey(data.candidate_public_Key)

        transaction_address = client.send_transaction(
            VoteInstruction(),
            [
                makeKeyPair(payerPrivateKey).public_key,
                owner_keypair.public_key,
                voter_public_key,
                candidate_public_Key,
                makePublicKey(sysvar_rent),
                makePublicKey(system_program),
            ],
            [
                makeKeyPair(payerPrivateKey),
                owner_keypair
            ]
        )

        return {
            "transaction_address": transaction_address,
            "voter_public_key": bs58.encode(voter_public_key.byte_value),
            "candidate_public_Key": bs58.encode(candidate_public_Key.byte_value),
        }

    return make_response_auto_catch(tryfcn)

# Get account data
@app.get("/get-voter-data")
async def get_voter_data(public_key: str):
    return make_response_auto_catch(lambda: client.get_account_data(PublicKey(public_key), VoterData, [8, 0]))

@app.get("/get-candidate-data")
async def get_candidate_data(public_key: str):
    return make_response_auto_catch(lambda: client.get_account_data(PublicKey(public_key), CandidateData, [8, 0]))

# Common API
@app.post("/convert-keypair-to-private-key")
async def convert_keypair_to_private_key(file: UploadFile):
    # Bytes to string
    result = file.file.read()
    keypair_json = json.loads(result)
    keypair_bytes = bytes(keypair_json)
    return {
        "public_key": bs58.encode(keypair_bytes[32:]),
        "private_key": bs58.encode(keypair_bytes),
    }

@app.get("/get-info")
async def get_info(public_key: str):
    return make_response_auto_catch(lambda: client.get_account_info(PublicKey(public_key)))

@app.get("/get-balance")
async def get_balance(public_key: str):
    return make_response_auto_catch(client.get_balance(public_key))

@app.post("/airdrop")
async def airdrop(public_key: str, amount: int = 1):
    return make_response_auto_catch(client.drop_sol(public_key, amount))

# Run
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=openPortAPI)

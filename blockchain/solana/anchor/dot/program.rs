#![allow(unused_imports)]
#![allow(unused_variables)]
#![allow(unused_mut)]
use crate::{id, seahorse_util::*};
use anchor_lang::{prelude::*, solana_program};
use anchor_spl::token::{self, Mint, Token, TokenAccount};
use std::{cell::RefCell, rc::Rc};

#[account]
#[derive(Debug)]
pub struct Candidate {
    pub owner: Pubkey,
    pub num_votes: u64,
}

impl<'info, 'entrypoint> Candidate {
    pub fn load(
        account: &'entrypoint mut Box<Account<'info, Self>>,
        programs_map: &'entrypoint ProgramsMap<'info>,
    ) -> Mutable<LoadedCandidate<'info, 'entrypoint>> {
        let owner = account.owner.clone();
        let num_votes = account.num_votes;

        Mutable::new(LoadedCandidate {
            __account__: account,
            __programs__: programs_map,
            owner,
            num_votes,
        })
    }

    pub fn store(loaded: Mutable<LoadedCandidate>) {
        let mut loaded = loaded.borrow_mut();
        let owner = loaded.owner.clone();

        loaded.__account__.owner = owner;

        let num_votes = loaded.num_votes;

        loaded.__account__.num_votes = num_votes;
    }
}

#[derive(Debug)]
pub struct LoadedCandidate<'info, 'entrypoint> {
    pub __account__: &'entrypoint mut Box<Account<'info, Candidate>>,
    pub __programs__: &'entrypoint ProgramsMap<'info>,
    pub owner: Pubkey,
    pub num_votes: u64,
}

#[account]
#[derive(Debug)]
pub struct Voter {
    pub owner: Pubkey,
    pub cccd_sha256: [u8; 32],
    pub vote_who: Pubkey,
    pub voted: bool,
}

impl<'info, 'entrypoint> Voter {
    pub fn load(
        account: &'entrypoint mut Box<Account<'info, Self>>,
        programs_map: &'entrypoint ProgramsMap<'info>,
    ) -> Mutable<LoadedVoter<'info, 'entrypoint>> {
        let owner = account.owner.clone();
        let cccd_sha256 = Mutable::new(account.cccd_sha256.clone());
        let vote_who = account.vote_who.clone();
        let voted = account.voted.clone();

        Mutable::new(LoadedVoter {
            __account__: account,
            __programs__: programs_map,
            owner,
            cccd_sha256,
            vote_who,
            voted,
        })
    }

    pub fn store(loaded: Mutable<LoadedVoter>) {
        let mut loaded = loaded.borrow_mut();
        let owner = loaded.owner.clone();

        loaded.__account__.owner = owner;

        let cccd_sha256 = loaded.cccd_sha256.borrow().clone();

        loaded.__account__.cccd_sha256 = cccd_sha256;

        let vote_who = loaded.vote_who.clone();

        loaded.__account__.vote_who = vote_who;

        let voted = loaded.voted.clone();

        loaded.__account__.voted = voted;
    }
}

#[derive(Debug)]
pub struct LoadedVoter<'info, 'entrypoint> {
    pub __account__: &'entrypoint mut Box<Account<'info, Voter>>,
    pub __programs__: &'entrypoint ProgramsMap<'info>,
    pub owner: Pubkey,
    pub cccd_sha256: Mutable<[u8; 32]>,
    pub vote_who: Pubkey,
    pub voted: bool,
}

pub fn init_candidate_handler<'info>(
    mut payer: SeahorseSigner<'info, '_>,
    mut owner: SeahorseSigner<'info, '_>,
    mut candidate: Empty<Mutable<LoadedCandidate<'info, '_>>>,
) -> () {
    let mut candidate = candidate.account.clone();

    assign!(candidate.borrow_mut().owner, owner.key());

    assign!(candidate.borrow_mut().num_votes, 0);
}

pub fn init_voter_handler<'info>(
    mut payer: SeahorseSigner<'info, '_>,
    mut owner: SeahorseSigner<'info, '_>,
    mut voter: Empty<Mutable<LoadedVoter<'info, '_>>>,
    mut cccd_sha256: [u8; 32],
) -> () {
    let mut voter = voter.account.clone();

    assign!(voter.borrow_mut().owner, owner.key());

    assign!(voter.borrow_mut().cccd_sha256, Mutable::<[u8; 32]>::new(cccd_sha256));
}

pub fn vote_handler<'info>(
    mut payer: SeahorseSigner<'info, '_>,
    mut voter_signer: SeahorseSigner<'info, '_>,
    mut voter: Mutable<LoadedVoter<'info, '_>>,
    mut candidate: Mutable<LoadedCandidate<'info, '_>>,
) -> () {
    if !(!voter.borrow().voted) {
        panic!("Voter has already voted");
    }

    if !(voter_signer.key() == voter.borrow().owner) {
        panic!("Voter is not the owner");
    }

    assign!(
        candidate.borrow_mut().num_votes,
        candidate.borrow().num_votes + 1
    );

    assign!(voter.borrow_mut().voted, true);

    assign!(
        voter.borrow_mut().vote_who,
        candidate.borrow().__account__.key()
    );
}

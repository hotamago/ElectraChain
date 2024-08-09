#![allow(unused_imports)]
#![allow(unused_variables)]
#![allow(unused_mut)]

pub mod dot;

use anchor_lang::prelude::*;
use anchor_spl::{
    associated_token::{self, AssociatedToken},
    token::{self, Mint, Token, TokenAccount},
};

use dot::program::*;
use std::{cell::RefCell, rc::Rc};

declare_id!("Exv9m3s2wcds1ajLMY9zMFhwdRcrX3FZyvWUSVdkUQxg");

pub mod seahorse_util {
    use super::*;

    #[cfg(feature = "pyth-sdk-solana")]
    pub use pyth_sdk_solana::{load_price_feed_from_account_info, PriceFeed};
    use std::{collections::HashMap, fmt::Debug, ops::Deref};

    pub struct Mutable<T>(Rc<RefCell<T>>);

    impl<T> Mutable<T> {
        pub fn new(obj: T) -> Self {
            Self(Rc::new(RefCell::new(obj)))
        }
    }

    impl<T> Clone for Mutable<T> {
        fn clone(&self) -> Self {
            Self(self.0.clone())
        }
    }

    impl<T> Deref for Mutable<T> {
        type Target = Rc<RefCell<T>>;

        fn deref(&self) -> &Self::Target {
            &self.0
        }
    }

    impl<T: Debug> Debug for Mutable<T> {
        fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
            write!(f, "{:?}", self.0)
        }
    }

    impl<T: Default> Default for Mutable<T> {
        fn default() -> Self {
            Self::new(T::default())
        }
    }

    impl<T: Clone> Mutable<Vec<T>> {
        pub fn wrapped_index(&self, mut index: i128) -> usize {
            if index >= 0 {
                return index.try_into().unwrap();
            }

            index += self.borrow().len() as i128;

            return index.try_into().unwrap();
        }
    }

    impl<T: Clone, const N: usize> Mutable<[T; N]> {
        pub fn wrapped_index(&self, mut index: i128) -> usize {
            if index >= 0 {
                return index.try_into().unwrap();
            }

            index += self.borrow().len() as i128;

            return index.try_into().unwrap();
        }
    }

    #[derive(Clone)]
    pub struct Empty<T: Clone> {
        pub account: T,
        pub bump: Option<u8>,
    }

    #[derive(Clone, Debug)]
    pub struct ProgramsMap<'info>(pub HashMap<&'static str, AccountInfo<'info>>);

    impl<'info> ProgramsMap<'info> {
        pub fn get(&self, name: &'static str) -> AccountInfo<'info> {
            self.0.get(name).unwrap().clone()
        }
    }

    #[derive(Clone, Debug)]
    pub struct WithPrograms<'info, 'entrypoint, A> {
        pub account: &'entrypoint A,
        pub programs: &'entrypoint ProgramsMap<'info>,
    }

    impl<'info, 'entrypoint, A> Deref for WithPrograms<'info, 'entrypoint, A> {
        type Target = A;

        fn deref(&self) -> &Self::Target {
            &self.account
        }
    }

    pub type SeahorseAccount<'info, 'entrypoint, A> =
        WithPrograms<'info, 'entrypoint, Box<Account<'info, A>>>;

    pub type SeahorseSigner<'info, 'entrypoint> = WithPrograms<'info, 'entrypoint, Signer<'info>>;

    #[derive(Clone, Debug)]
    pub struct CpiAccount<'info> {
        #[doc = "CHECK: CpiAccounts temporarily store AccountInfos."]
        pub account_info: AccountInfo<'info>,
        pub is_writable: bool,
        pub is_signer: bool,
        pub seeds: Option<Vec<Vec<u8>>>,
    }

    #[macro_export]
    macro_rules! seahorse_const {
        ($ name : ident , $ value : expr) => {
            macro_rules! $name {
                () => {
                    $value
                };
            }

            pub(crate) use $name;
        };
    }

    #[macro_export]
    macro_rules! assign {
        ($ lval : expr , $ rval : expr) => {{
            let temp = $rval;

            $lval = temp;
        }};
    }

    #[macro_export]
    macro_rules! index_assign {
        ($ lval : expr , $ idx : expr , $ rval : expr) => {
            let temp_rval = $rval;
            let temp_idx = $idx;

            $lval[temp_idx] = temp_rval;
        };
    }

    pub(crate) use assign;

    pub(crate) use index_assign;

    pub(crate) use seahorse_const;
}

#[program]
mod compi {
    use super::*;
    use seahorse_util::*;
    use std::collections::HashMap;

    #[derive(Accounts)]
    pub struct InitCandidate<'info> {
        #[account(mut)]
        pub payer: Signer<'info>,
        #[account(mut)]
        pub owner: Signer<'info>,
        # [account (init , space = std :: mem :: size_of :: < dot :: program :: Candidate > () + 8 , payer = payer , seeds = [owner . key () . as_ref () , "candidate" . as_bytes () . as_ref ()] , bump)]
        pub candidate: Box<Account<'info, dot::program::Candidate>>,
        pub rent: Sysvar<'info, Rent>,
        pub system_program: Program<'info, System>,
    }

    pub fn init_candidate(ctx: Context<InitCandidate>) -> Result<()> {
        let mut programs = HashMap::new();

        programs.insert(
            "system_program",
            ctx.accounts.system_program.to_account_info(),
        );

        let programs_map = ProgramsMap(programs);
        let payer = SeahorseSigner {
            account: &ctx.accounts.payer,
            programs: &programs_map,
        };

        let owner = SeahorseSigner {
            account: &ctx.accounts.owner,
            programs: &programs_map,
        };

        let candidate = Empty {
            account: dot::program::Candidate::load(&mut ctx.accounts.candidate, &programs_map),
            bump: Some(ctx.bumps.candidate),
        };

        init_candidate_handler(payer.clone(), owner.clone(), candidate.clone());

        dot::program::Candidate::store(candidate.account);

        return Ok(());
    }

    #[derive(Accounts)]
    # [instruction (cccd_sha256: [u8; 32])]
    pub struct InitVoter<'info> {
        #[account(mut)]
        pub payer: Signer<'info>,
        #[account(mut)]
        pub owner: Signer<'info>,
        # [account (init , space = std :: mem :: size_of :: < dot :: program :: Voter > () + 8 , payer = payer , seeds = [owner . key () . as_ref () , "voter" . as_bytes () . as_ref ()] , bump)]
        pub voter: Box<Account<'info, dot::program::Voter>>,
        pub rent: Sysvar<'info, Rent>,
        pub system_program: Program<'info, System>,
    }

    pub fn init_voter(
        ctx: Context<InitVoter>,
        cccd_sha256: [u8; 32],
    ) -> Result<()> {
        let mut programs = HashMap::new();

        programs.insert(
            "system_program",
            ctx.accounts.system_program.to_account_info(),
        );

        let programs_map = ProgramsMap(programs);
        let payer = SeahorseSigner {
            account: &ctx.accounts.payer,
            programs: &programs_map,
        };

        let owner = SeahorseSigner {
            account: &ctx.accounts.owner,
            programs: &programs_map,
        };

        let voter = Empty {
            account: dot::program::Voter::load(&mut ctx.accounts.voter, &programs_map),
            bump: Some(ctx.bumps.voter),
        };

        init_voter_handler(
            payer.clone(),
            owner.clone(),
            voter.clone(),
            cccd_sha256,
        );

        dot::program::Voter::store(voter.account);

        return Ok(());
    }

    #[derive(Accounts)]
    pub struct Vote<'info> {
        #[account(mut)]
        pub payer: Signer<'info>,
        #[account(mut)]
        pub voter_signer: Signer<'info>,
        #[account(mut)]
        pub voter: Box<Account<'info, dot::program::Voter>>,
        #[account(mut)]
        pub candidate: Box<Account<'info, dot::program::Candidate>>,
    }

    pub fn vote(ctx: Context<Vote>) -> Result<()> {
        let mut programs = HashMap::new();
        let programs_map = ProgramsMap(programs);
        let payer = SeahorseSigner {
            account: &ctx.accounts.payer,
            programs: &programs_map,
        };

        let voter_signer = SeahorseSigner {
            account: &ctx.accounts.voter_signer,
            programs: &programs_map,
        };

        let voter = dot::program::Voter::load(&mut ctx.accounts.voter, &programs_map);
        let candidate = dot::program::Candidate::load(&mut ctx.accounts.candidate, &programs_map);

        vote_handler(
            payer.clone(),
            voter_signer.clone(),
            voter.clone(),
            candidate.clone(),
        );

        dot::program::Voter::store(voter);

        dot::program::Candidate::store(candidate);

        return Ok(());
    }
}

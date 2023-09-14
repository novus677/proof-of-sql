use clap::Parser;
use halo2_base::gates::{GateChip, GateInstructions};
use halo2_base::safe_types::{RangeChip, RangeInstructions};
use halo2_base::utils::ScalarField;
use halo2_base::AssignedValue;
#[allow(unused_imports)]
use halo2_base::{
    Context,
    QuantumCell::{Constant, Existing, Witness},
};
use proof_of_sql::scaffold::cmd::Cli;
use proof_of_sql::scaffold::run;
use serde::{Deserialize, Serialize};
use std::env::var;

const NUM_COLS: usize = 2;

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct CircuitInput {
    pub db: [Vec<u64>; NUM_COLS],
}

fn select_indices<F: ScalarField>(
    ctx: &mut Context<F>,
    input: CircuitInput,
    make_public: &mut Vec<AssignedValue<F>>,
) {
    let lookup_bits =
        var("LOOKUP_BITS").unwrap_or_else(|_| panic!("LOOKUP_BITS not set")).parse().unwrap();
    let db: Vec<Vec<AssignedValue<F>>> = input
        .db
        .into_iter()
        .map(|col| ctx.assign_witnesses(col.into_iter().map(|x| F::from(x))))
        .collect();

    let range = RangeChip::default(lookup_bits);
}

fn main() {
    env_logger::init();
    let args = Cli::parse();
    run(select_indices, args);
}

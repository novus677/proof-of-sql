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
    let intermediate9: Vec<AssignedValue<F>> =
        db[0].iter().zip(db[1].iter()).map(|(&x, &y)| range.gate().is_equal(ctx, x, y)).collect();
    let val4 = ctx.load_constant(F::from(0));
    let intermediate10: Vec<AssignedValue<F>> =
        db[0].iter().map(|&x| range.gate().is_equal(ctx, x, val4)).collect();
    let intermediate11: Vec<AssignedValue<F>> = intermediate9
        .iter()
        .zip(intermediate10.iter())
        .map(|(&x, &y)| range.gate().or(ctx, x, y))
        .collect();
    let val6 = ctx.load_constant(F::from(0));
    let intermediate12: Vec<AssignedValue<F>> = db[1]
        .iter()
        .map(|&x| {
            let plus_one = range.gate().add(ctx, x, Constant(F::one()));
            range.is_less_than(ctx, val6, plus_one, 10)
        })
        .collect();
    let intermediate13: Vec<AssignedValue<F>> = intermediate11
        .iter()
        .zip(intermediate12.iter())
        .map(|(&x, &y)| range.gate().and(ctx, x, y))
        .collect();
    let val8 = ctx.load_constant(F::from(5));
    let intermediate14: Vec<AssignedValue<F>> =
        db[1].iter().map(|&x| range.is_less_than(ctx, x, val8, 10)).collect();
    let intermediate15: Vec<AssignedValue<F>> = intermediate13
        .iter()
        .zip(intermediate14.iter())
        .map(|(&x, &y)| range.gate().and(ctx, x, y))
        .collect();
}

fn main() {
    env_logger::init();
    let args = Cli::parse();
    run(select_indices, args);
}

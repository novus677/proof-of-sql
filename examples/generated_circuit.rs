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

    let intermediate2: Vec<AssignedValue<F>> =
        db[0].iter().zip(db[1].iter()).map(|(&x, &y)| range.gate().is_equal(ctx, x, y)).collect();
    let val4 = ctx.load_constant(F::from(0));
    let intermediate5: Vec<AssignedValue<F>> =
        db[0].iter().map(|&x| range.gate().is_equal(ctx, x, val4)).collect();
    let intermediate6: Vec<AssignedValue<F>> = intermediate2
        .iter()
        .zip(intermediate5.iter())
        .map(|(&x, &y)| range.gate().or(ctx, x, y))
        .collect();
    let intermediate7 = intermediate6;
    let val9 = ctx.load_constant(F::from(0));
    let intermediate10: Vec<AssignedValue<F>> = db[1]
        .iter()
        .map(|&x| {
            let plus_one = range.gate().add(ctx, x, Constant(F::one()));
            range.is_less_than(ctx, val9, plus_one, 10)
        })
        .collect();
    let intermediate11: Vec<AssignedValue<F>> = intermediate7
        .iter()
        .zip(intermediate10.iter())
        .map(|(&x, &y)| range.gate().and(ctx, x, y))
        .collect();
    let val13 = ctx.load_constant(F::from(5));
    let intermediate14: Vec<AssignedValue<F>> =
        db[1].iter().map(|&x| range.is_less_than(ctx, x, val13, 10)).collect();
    let out: Vec<AssignedValue<F>> = intermediate11
        .iter()
        .zip(intermediate14.iter())
        .map(|(&x, &y)| range.gate().and(ctx, x, y))
        .collect();

    println!("out: {:?}", out.iter().map(|x| x.value()).collect::<Vec<_>>())
}

fn main() {
    env_logger::init();
    let args = Cli::parse();
    run(select_indices, args);
}

#include <stdlib.h>
#include <fstream>
#include <cassert>

#include "dynein_struct.h"

/* ********************* ONEBOUND DYNEIN FUNCTIONS ************************** */

Dynein_onebound::Dynein_onebound(double bba_init, double bma_init,
				 double uma_init, double uba_init,
				 double bbx_init, double bby_init,
				 State s, onebound_forces *internal_test,
				 onebound_forces *brownian_test,
				 onebound_equilibrium_angles* eq_angles,
                                 MTRand* mtrand) {
  bbx = bbx_init;
  bby = bby_init;

  bba = bba_init;
  bma = bma_init;
  uma = uma_init;
  uba = uba_init;

  state = s;
  internal_testcase = internal_test;
  brownian_testcase = brownian_test;

  if (eq_angles) {
    eq = *eq_angles; // use test angles
  } else {
    eq = onebound_post_powerstroke_internal_angles; // use experimental angles
  }

  rand = mtrand;

  update_velocities();
}

Dynein_onebound::Dynein_onebound(Dynein_bothbound* old_dynein, MTRand* mtrand, State s) {
  if (s == State::NEARBOUND) {
    bbx = old_dynein->get_nbx();
    bby = 0;

    state = State::NEARBOUND;

    bba = old_dynein->get_nba();
    bma = old_dynein->get_nma() + old_dynein->get_nba() - M_PI;
    uma = old_dynein->get_fma() + old_dynein->get_fba() - M_PI;
    uba = old_dynein->get_fba();

  } else {
    bbx = old_dynein->get_fbx();
    bby = 0;

    state = State::FARBOUND;

    bba = old_dynein->get_fba();
    bma = old_dynein->get_fma() + old_dynein->get_fba() - M_PI;
    uma = old_dynein->get_nma() + old_dynein->get_nba() - M_PI;
    uba = old_dynein->get_nba();
  }

  internal_testcase = NULL;
  brownian_testcase = NULL;

  rand = mtrand;

  update_velocities();
}

void Dynein_onebound::update_brownian_forces() {
  if (brownian_testcase) {
    r = *brownian_testcase; // just copy over forces!
  } else {
    rand->gauss2(gb*sqrt(2*kb*T/(gb*dt)), &r.bbx, &r.bby);
    rand->gauss2(gm*sqrt(2*kb*T/(gm*dt)), &r.bmx, &r.bmy);
    rand->gauss2(gt*sqrt(2*kb*T/(gt*dt)), &r.tx, &r.ty);
    rand->gauss2(gm*sqrt(2*kb*T/(gm*dt)), &r.umx, &r.umy);
    rand->gauss2(gb*sqrt(2*kb*T/(gb*dt)), &r.ubx, &r.uby);
  }
}

void Dynein_onebound::update_internal_forces() {
  if (internal_testcase) {
    f = *internal_testcase;
  } else {
    f.bbx = 0;     f.bby = 0;     // Initialize forces to zero
    f.bmx = 0;     f.bmy = 0;
    f.tx  = 0;     f.ty  = 0;
    f.umx = 0;     f.umy = 0;
    f.ubx = 0;     f.uby = 0;

    double T, f1, f2, f1x, f1y, f2x, f2y;

    T = cb*(bba - eq.bba);
    PE_bba = 0.5*cb*(bba - eq.bba)*(bba - eq.bba);
    f2 = T/Ls;
    f2x = f2 * sin(bba);
    f2y = f2 * -cos(bba);
    f.bmx += f2x;
    f.bmy += f2y;
    f.bbx += -f2x; // Equal and opposite forces!  :)
    f.bby += -f2y; // Equal and opposite forces!  :)

    T = cm*((bma + M_PI - bba) - eq.bba);
    PE_bma = 0.5*cm*((bma + M_PI - bba) - eq.bba)*((bma + M_PI - bba) - eq.bba);
    f1 = T/Ls;
    f2 = T/Lt;
    f1x = f1 * sin(bba);
    f1y = f1 * -cos(bba);
    f2x = f2 * sin(bma);
    f2y = f2 * -cos(bma);
    f.bbx += f1x;
    f.bby += f1y;
    f.tx  += f2x;
    f.ty  += f2y;
    f.bmx += -(f1x + f2x);
    f.bmy += -(f1y + f2y);

    T = ct*(uma - bma - eq.ta);  //-- this used to be the negation, this is right?
    PE_ta = 0.5*ct*(uma - bma - eq.ta)*(uma - bma - eq.ta);
    f1 = T / Lt;
    f2 = T / Lt;
    f1x = f1 * sin(bma);
    f1y = f1 * -cos(bma);
    f2x = f2 * -sin(uma);  // not sure if these angles are right?
    f2y = f2 * cos(uma);
    f.bmx += f1x;
    f.bmy += f1y;
    f.umx += f2x;
    f.umy += f2y;
    f.tx  += -(f1x + f2x);
    f.ty  += -(f1y + f2y);

    T = cm*((uma + M_PI - uba) - eq.uma);
    PE_uma = 0.5*cm*((uma + M_PI - uba) - eq.uma)*((uma + M_PI - uba) - eq.uma);
    f1 = T / Lt;
    f2 = T / Ls;
    f1x = f1 * sin(uma);
    f1y = f1 * -cos(uma);
    f2x = f2 * sin(uba);
    f2y = f2 * -cos(uba);
    f.tx  += f1x;
    f.ty  += f1y;
    f.ubx += f2x;
    f.uby += f2y;
    f.umx += -(f1x + f2x);
    f.umy += -(f1y + f2y);

    if (get_bmy() < 0) f.bmy += MICROTUBULE_REPULSION_FORCE * fabs(get_bmy());
    if (get_ty()  < 0) f.ty  += MICROTUBULE_REPULSION_FORCE * fabs(get_ty());
    if (get_umy() < 0) f.umy += MICROTUBULE_REPULSION_FORCE * fabs(get_umy());
    if (get_uby() < 0) f.uby += MICROTUBULE_REPULSION_FORCE * fabs(get_uby());
  }
}

// void Dynein_onebound::switch_to_bothbound() {
//   double temp_nma;
//   double temp_fma;

//   if (state == NEARBOUND) {
//     temp_nma = M_PI + bma - bba;
//     temp_fma = M_PI + uma - uba;
//     nbx = get_bbx();
//     L = fbx - nbx;
//   } else {
//     temp_nma = M_PI + uma - uba;
//     temp_fma = M_PI + bma - bba;
//     nbx = get_fbx();
//     L = bbx - fbx;
//   }

//   distance_traveled += fabs(get_ubx() - get_bbx());
//   steps++;

//   state = BOTHBOUND;
//   nma = temp_nma;
//   fma = temp_fma;
// }

// void Dynein_onebound::switch_to_nearbound() {
//   //nearbound -> bma is nma
//   double temp_bba = get_nba();
//   double temp_bma = nma;
//   double temp_uma = fma;
//   double temp_uba = get_fba();

//   bbx = get_nbx();
//   bby = 0;

//   bba = temp_bba;
//   bma = temp_bma;
//   uma = temp_uma;
//   uba = temp_uba;

//   state = NEARBOUND;
// }

// void Dynein_onebound::switch_to_farbound() {
//   //nearbound -> bma is fma
//   double temp_bba = get_fba();
//   double temp_bma = fma;
//   double temp_uma = nma;
//   double temp_uba = get_nba();

//   bbx = get_fbx();
//   bby = 0;

//   bba = temp_bba;
//   bma = temp_bma;
//   uma = temp_uma;
//   uba = temp_uba;

//   state = FARBOUND;
// }

void Dynein_onebound::update_velocities() {
  update_internal_forces();
  update_brownian_forces();

  float A1, A2, A3, A4;  // Start solving for velocities with matrix solution in derivation.pdf
  float B1, B2, B3, B4;
  float C1, C2, C3, C4;
  float D1, D2, D3, D4;
  float X1, X2, X3, X4;
  float Nbb, Nml, Nmr, Nbr;
  float D;

  A1 = -4*Ls;
  A2 = -3*Lt*(sin(bma)*sin(bba) + cos(bma)*cos(bba));
  A3 = 2*Lt*(sin(uma)*sin(bba) + cos(uma)*cos(bba));
  A4 = Ls*(sin(uba)*sin(bba) + cos(uba)*cos(bba));
  B1 = -3*Ls*(sin(bba)*sin(bma) + cos(bba)*cos(bma));
  B2 = -3*Lt;
  B3 = +2*Lt*(sin(uma)*sin(bma) + cos(uma)*cos(bma));
  B4 = +Ls*(sin(uba)*sin(bma) + cos(uba)*cos(bma));
  C1 = -2*Ls*(sin(bba)*sin(uma) + cos(bba)*cos(uma));
  C2 = -2*Lt*(sin(bma)*sin(uma) + cos(bma)*cos(uma));
  C3 = 2*Lt;
  C4 = Ls*(sin(uba)*sin(uma) + cos(uba)*cos(uma));
  D1 = Ls*(cos(uba)*cos(bba) + sin(uba)*sin(bba));
  D2 = Lt*(cos(uba)*cos(bma) + sin(uba)*sin(bma));
  D3 = -Lt*(cos(uba)*cos(uma) + sin(uba)*sin(uma));
  D4 = -Ls;

  X1 = (- 1/gm*f.bmy - 1/gt*f.ty - 1/gm*f.umy - 1/gb*f.uby - r.bmy/gm - r.ty/gt - r.umy/gm -
	r.uby/gb)*cos(bba) +( 1/gm*f.bmx + 1/gt*f.tx + 1/gm*f.umx + 1/gb*f.ubx + r.bmx/gm +
	r.tx/gt + r.umx/gm + r.ubx/gb )*sin(bba);

  X2 = (-1/gt*f.ty - 1/gm*f.umy - 1/gb*f.uby - r.ty/gt - r.umy/gm - r.uby/gb)*cos(bma) +
    (1/gt*f.tx + 1/gm*f.umx + 1/gb*f.ubx + r.tx/gt + r.umx/gm + r.ubx/gb)*sin(bma);

  X3 = (-r.umy/gm -r.uby/gb - 1/gm*f.umy - 1/gb*f.uby)*cos(uma) + (r.umx/gm + r.ubx/gb +
	 1/gm*f.umx + 1/gb*f.ubx)*sin(uma);

  X4 = (r.uby/gb + 1/gb*f.uby)*cos(uba) - (r.ubx/gb + 1/gb*f.ubx)*sin(uba);

  Nbb = (-B2*C4*D3*X1 + B2*C3*D4*X1 + A4*C3*D2*X2 - A3*C4*D2*X2 - A4*C2*D3*X2 + A2*C4*D3*X2
	 +A3*C2*D4*X2 - A2*C3*D4*X2 + A4*B2*D3*X3 - A3*B2*D4*X3 - A4*B2*C3*X4 + A3*B2*C4*X4
	 +B4*(-C3*D2*X1 + C2*D3*X1 + A3*D2*X3 - A2*D3*X3 - A3*C2*X4 + A2*C3*X4)
	 +B3*(C4*D2*X1 - C2*D4*X1 - A4*D2*X3 + A2*D4*X3 + A4*C2*X4 - A2*C4*X4));

  Nml = (B1*C4*D3*X1 - B1*C3*D4*X1 - A4*C3*D1*X2 + A3*C4*D1*X2 + A4*C1*D3*X2 - A1*C4*D3*X2
	 -A3*C1*D4*X2 + A1*C3*D4*X2 - A4*B1*D3*X3 + A3*B1*D4*X3 + A4*B1*C3*X4 - A3*B1*C4*X4
	 +B4*(C3*D1*X1 - C1*D3*X1 - A3*D1*X3 + A1*D3*X3 + A3*C1*X4 - A1*C3*X4)
	 +B3*(-C4*D1*X1 + C1*D4*X1 + A4*D1*X3 - A1*D4*X3 - A4*C1*X4 + A1*C4*X4));

  Nmr = (-B1*C4*D2*X1 + B1*C2*D4*X1 + A4*C2*D1*X2 - A2*C4*D1*X2 - A4*C1*D2*X2 + A1*C4*D2*X2
	 +A2*C1*D4*X2 - A1*C2*D4*X2 + A4*B1*D2*X3 - A2*B1*D4*X3 - A4*B1*C2*X4 + A2*B1*C4*X4
	 +B4*(-C2*D1*X1 + C1*D2*X1 + A2*D1*X3 - A1*D2*X3 - A2*C1*X4 + A1*C2*X4)
	 +B2*(C4*D1*X1 - C1*D4*X1 - A4*D1*X3 + A1*D4*X3 + A4*C1*X4 - A1*C4*X4));

  Nbr = (B1*C3*D2*X1 - B1*C2*D3*X1 - A3*C2*D1*X2 + A2*C3*D1*X2 + A3*C1*D2*X2 - A1*C3*D2*X2
	 -A2*C1*D3*X2 + A1*C2*D3*X2 - A3*B1*D2*X3 + A2*B1*D3*X3 + A3*B1*C2*X4 - A2*B1*C3*X4
	 +B3*(C2*D1*X1 - C1*D2*X1 - A2*D1*X3 + A1*D2*X3 + A2*C1*X4 - A1*C2*X4)
	 +B2*(-C3*D1*X1 + C1*D3*X1 + A3*D1*X3 - A1*D3*X3 - A3*C1*X4 + A1*C3*X4));

  D = A2*B4*C3*D1 - A2*B3*C4*D1 - A1*B4*C3*D2 + A1*B3*C4*D2 - A2*B4*C1*D3 + A1*B4*C2*D3
         +A2*B1*C4*D3 - A1*B2*C4*D3 + A4*(B3*C2*D1 - B2*C3*D1 - B3*C1*D2 + B1*C3*D2 + B2*C1*D3
         -B1*C2*D3)+ A2*B3*C1*D4 - A1*B3*C2*D4 - A2*B1*C3*D4 + A1*B2*C3*D4
         +A3*(-B4*C2*D1 + B2*C4*D1 + B4*C1*D2 - B1*C4*D2 - B2*C1*D4 + B1*C2*D4);

  assert(D != 0);

  d_bba = Nbb/D;
  d_bma = Nml/D;
  d_uma = Nmr/D;
  d_uba = Nbr/D;
}

double Dynein_onebound::get_binding_rate() {
  if (get_uby() < MICROTUBULE_BINDING_DISTANCE) {
    double U_bb = Dynein_bothbound(this, rand).get_PE();
    double U_ob = get_PE();
    return binding_preexponential_factor*exp(-(U_bb - U_ob)/kb/T); // per second
  } else {
    return 0;
  }
}

double Dynein_onebound::get_unbinding_rate() {
  if (f.bby + r.bby >= ONEBOUND_UNBINDING_FORCE) {
    return 1.0;
  } else return 0.0;
}

/*** Set positions, velocities and forces ***/
void Dynein_onebound::set_bbx(double d) {   // onebound
  bbx = d;
}

void Dynein_onebound::set_bby(double d) {   // onebound
  bby = d;
}

void Dynein_onebound::set_bba(double d) {   // onebound
  bba = d;
}

void Dynein_onebound::set_bma(double d) {   // onebound
  bma = d;
}

void Dynein_onebound::set_uma(double d) {   // onebound
  uma = d;
}

void Dynein_onebound::set_uba(double d) {   // onebound
  uba = d;
}

/*** Angular Velocities ***/

double Dynein_onebound::get_d_bba() {
  return d_bba;
}

double Dynein_onebound::get_d_bma() {
  return d_bma;
}

double Dynein_onebound::get_d_uma() {
  return d_uma;
}

double Dynein_onebound::get_d_uba() {
  return d_uba;
}

/*** Get coordinates ***/

double Dynein_onebound::get_bbx() {
  return bbx;
}

double Dynein_onebound::get_bby(){
  return bby;
}

double Dynein_onebound::get_bmx() {
  return Ls * cos(get_bba()) + bbx;
}

double Dynein_onebound::get_bmy(){
  return Ls * sin(get_bba()) + bby;
}

double Dynein_onebound::get_tx() {
  return Ls * cos(get_bba()) + Lt * cos(get_bma()) + bbx;
}

double Dynein_onebound::get_ty(){
  return Ls * sin(get_bba()) + Lt * sin(get_bma()) + bby;
}

double Dynein_onebound::get_umx() {
  return Ls * cos(get_bba()) + Lt * cos(get_bma()) - Lt * cos(get_uma()) + bbx;
}

double Dynein_onebound::get_umy(){
  return Ls * sin(get_bba()) + Lt * sin(get_bma()) - Lt * sin(get_uma()) + bby;
}

double Dynein_onebound::get_ubx() {
  return Ls * cos(get_bba()) + Lt * cos(get_bma())
    - Lt * cos(get_uma()) - Ls * cos(get_uba()) + bbx;
}

double Dynein_onebound::get_uby(){
  return Ls * sin(get_bba()) + Lt * sin(get_bma())
    - Lt * sin(get_uma()) - Ls * sin(get_uba()) + bby;
}

/*** Get Cartesian Velocities ***/

double Dynein_onebound::get_d_bbx() {
  return 0;
}

double Dynein_onebound::get_d_bmx() {
  return Ls * d_bba * -sin(bba);
}

double Dynein_onebound::get_d_tx() {
  return Lt * d_bma * -sin(bma) + get_d_bmx();
}

double Dynein_onebound::get_d_umx() {
  return Lt * d_uma * sin(uma) + get_d_tx();
}

double Dynein_onebound::get_d_ubx() {
  return Ls * d_uba * sin(uba) + get_d_umx();
}

double Dynein_onebound::get_d_bby() {
  return 0;
}

double Dynein_onebound::get_d_bmy() {
    return Ls * d_bba * cos(bba);
}

double Dynein_onebound::get_d_ty() {
    return Lt * d_bma * cos(bma) + get_d_bmy();
}

double Dynein_onebound::get_d_umy() {
    return Lt * d_uma * -cos(uma) + get_d_ty();
}

double Dynein_onebound::get_d_uby() {
  return Ls * d_uba * -cos(uba) + get_d_umy();
}

/*** Get forces, state ***/
onebound_forces Dynein_onebound::get_internal() {
  return f;
}

onebound_forces Dynein_onebound::get_brownian() {
  return r;
}

State Dynein_onebound::get_state() {
  return state;
}

/*** Get angles ***/

double Dynein_onebound::get_bba() {
  return bba;
}

double Dynein_onebound::get_bma() {
  return bma;
}

double Dynein_onebound::get_uma() {
  return uma;
}

double Dynein_onebound::get_uba() {
  return uba;
}

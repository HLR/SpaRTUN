left_(none,none).
right_(none,none).
above_(none,none).
below_(none,none).
front_(none,none).
behind_(none,none).
near_(none,none).
far_(none,none).
dc_(none,none).
ec_(none,none).
po_(none,none).
eq_(none,none).
tpp_(none,none).
ntpp_(none,none).
tppi_(none,none).
ntppi_(none,none).

%left_(circle,square).
%left_(square,oval).
%left_(rectangle,oval).

%left_(box1, box2).

%right_(rectangle,square).
%right_(dimond,oval).

%above_(square,oval).
%above_(box1, box2).
%below_(box3,box2).

%ntpp_(apple,box1).
%ntpp_(pear, box3).
%ntppi_(box2,grapes).
%ntppi_(room,box1).
%ntppi_(room,box2).
%dc_(box2,box1).
%eq_(apple1,apple).
%eq_(apple2,apple1).


%start_to_define_rules

%%reflexive reverse symmetry
%directional
left_1(X,Y) :- 
	left_(X,Y);
	right_(Y,X).
right_1(X,Y) :- 
	right_(X,Y);
	left_(Y,X).
below_1(X,Y) :- 
	below_(X,Y);
	above_(Y,X).
above_1(X,Y) :- 
	above_(X,Y);
	below_(Y,X).
front_1(X,Y) :- 
	front_(X,Y);
	behind_(Y,X).
behind_1(X,Y) :- 
	behind_(X,Y);
	front_(Y,X).

%topological
ntppi_1(X,Y) :- 
	ntppi_(X,Y);
	ntpp_(Y,X).
ntpp_1(X,Y) :- 
	ntpp_(X,Y);
	ntppi_(Y,X).
tppi_1(X,Y) :- 
	tppi_(X,Y);
	tpp_(Y,X).
tpp_1(X,Y) :- 
	tpp_(X,Y);
	tppi_(Y,X).
ec_1(X,Y) :- 
	ec_(X,Y);
	ec_(Y,X).
po_1(X,Y) :- 
	po_(X,Y);
	po_(Y,X).
dc_1(X,Y) :- 
	dc_(X,Y);
	dc_(Y,X).
eq_1(X,Y) :- 
	eq_(X,Y);
	eq_(Y,X).

%distantial
near_1(X,Y) :- 
	near_(X,Y);
	near_(Y,X).
far_1(X,Y) :- 
	far_(X,Y);
	far_(Y,X).

%ireflexive
%X \= Y :- 
%	left_(X,Y);
%	right_(X,Y);
%	below_(X,Y);
%	above_(X,Y);
%	front_(X,Y);
%	behind_(X,Y);
%	front_(Y,X);
%	near_(X,Y);
%	far_(X,Y);
%	ntppi_(X,Y);
%	ntpp_(X,Y);
%	tppi_(X,Y);
%	tpp_(X,Y);
%	ec_(X,Y);
%	po_(X,Y);
%	dc_(X,Y).



%not
%%objects doesnt have relations with themself
%directional
not(right_1(X,Y)) :- left_1(X,Y); X = Y.
not(left_1(X,Y)) :- right_1(X,Y); X = Y.
not(above_1(X,Y)) :- below_1(X,Y); X = Y.
not(below_1(X,Y)) :- above_1(X,Y); X = Y.
not(behind_1(X,Y)) :- front_1(X,Y); X = Y.
not(front_1(X,Y)) :- behind_1(X,Y); X = Y.


%not
%topological
not(ntppi_1(X,Y)) :- 
	ntpp_1(X,Y); 
	tppi_1(X,Y); 
	tpp_1(X,Y); 
	po_1(X,Y); 
	dc_1(X,Y); 
	eq_1(X,Y); 
	ec_1(X,Y);
	X = Y.
not(ntpp_1(X,Y)) :- 
	ntppi_1(X,Y); 
	tppi_1(X,Y); 
	tpp_1(X,Y); 
	po_1(X,Y); 
	dc_1(X,Y); 
	eq_1(X,Y); 
	ec_1(X,Y);
	X = Y.
not(tppi_1(X,Y)) :- 
	ntpp_1(X,Y); 
	ntppi_1(X,Y); 
	tpp_1(X,Y); 
	po_1(X,Y); 
	dc_1(X,Y); 
	eq_1(X,Y); 
	ec_1(X,Y);
	X = Y.
not(tpp_1(X,Y)) :- 
	ntpp_1(X,Y); 
	tppi_1(X,Y); 
	ntppi_1(X,Y); 
	po_1(X,Y); 
	dc_1(X,Y); 
	eq_1(X,Y); 
	ec_1(X,Y);
	X = Y.
not(ec_1(X,Y)) :- 
	ntppi_1(X,Y); 
	ntpp_1(X,Y); 
	tppi_1(X,Y); 
	tpp_1(X,Y); 
	po_1(X,Y); 
	dc_1(X,Y); 
	eq_1(X,Y);
	X = Y.
not(po_1(X,Y)) :- 
	ntppi_1(X,Y); 
	ntpp_1(X,Y); 
	tppi_1(X,Y); 
	tpp_1(X,Y); 
	dc_1(X,Y); 
	eq_1(X,Y); 
	ec_1(X,Y);
	X = Y.
not(dc_1(X,Y)) :- 
	ntppi_1(X,Y); 
	ntpp_1(X,Y); 
	tppi_1(X,Y); 
	tpp_1(X,Y); 
	po_1(X,Y); 
	eq_1(X,Y); 
	ec_1(X,Y);
	X = Y.
not(eq_1(X,Y)) :- 
	ntppi_1(X,Y); 
	ntpp_1(X,Y); 
	tppi_1(X,Y); 
	tpp_1(X,Y); 
	po_1(X,Y); 
	dc_1(X,Y); 
	ec_1(X,Y).

%not
%distantial
not(far_1(X,Y)) :- 
	near_1(X,Y);
	X = Y.
not(near_1(X,Y)) :- 
	far_1(X,Y);
	X = Y.




%transitivity
%combination_of_relational

left_2(X,Y) :-
	left_2(X,Y,[]).

left_2(X,Y, _) :-
	left_1(X,Y).

left_2(X,Z, Visited) :-
	left_1(X,Y), 
	Y \= X,
	\+ member(Y, Visited),
	left_2(Y,Z, [Y|Visited]),
	Y \= Z,
	X \= Z.

left_2_check(X,Y) :- left_2(X,Y), !.

right_2(X,Z) :- left_2(Z,X).

above_2(X,Y) :-
	above_2(X,Y,[]).

above_2(X,Y, _) :-
	above_1(X,Y).

above_2(X,Z, Visited) :-
	above_1(X,Y), 
	Y \= X, 
	\+ member(Y, Visited),
	above_2(Y,Z, [Y|Visited]),
	Y \= Z,
	X \= Z.

above_2_check(X,Y) :- above_2(X,Y), !.

below_2(X,Z) :- above_2(Z,X).


behind_2(X,Y) :-
	behind_2(X,Y,[]).

behind_2(X,Y, _) :-
	behind_1(X,Y).

behind_2(X,Z, Visited) :-
	behind_1(X,Y), 
	Y \= X, 
	\+ member(Y, Visited),
	behind_2(Y,Z, [Y|Visited]),
	Y \= Z,
	X \= Z.

behind_2_check(X,Y) :- behind_2(X,Y), !.

front_2(X,Z) :- behind_2(Z,X).


%transitivity
%combination_of_topological
%%transitivity on equal, tpp, tppi, ntpp, ntppi

eq_2_(X,Y) :-
	eq_2_(X,Y,[]).

eq_2_(X,Y, _) :-
	eq_1(X,Y).

eq_2_(X,Z, Visited) :-
	eq_1(X,Y),
	Y \=  X,
	\+ member(Y, Visited),
	eq_2_(Y,Z, [Y|Visited]),
	Y \= Z,
	X \= Z.

eq_2(X,Z) :- eq_2_(X,Z).

eq_2_check(X,Z) :- X \= Z, eq_2(X,Z), !.



dc_2_(X,Y) :- 
	dc_1(X,Y);
    dc_1(X,Z), eq_2_check(Y,Z);
    dc_1(Z,Y), eq_2(X,Z).
dc_2(X,Y) :- dc_2_(X,Y).

dc_2_check(X,Y) :- dc_2(X,Y), !.

ec_2_(X,Y) :- 
	ec_1(X,Y);
	ec_1(X,Z), eq_2_check(Y,Z);
	ec_1(Z,Y), eq_2(X,Z).
ec_2(X,Y) :- ec_2_(X,Y).

po_2_(X,Y) :- 
	po_1(X,Y);
	po_1(X,Z), eq_2_check(Y,Z);
	po_1(Z,Y), eq_2(X,Z).
po_2(X,Y) :- po_2_(X,Y).

tppi_2_(X,Y) :- 
	tppi_1(X,Y);
	tppi_1(X,Z), eq_2_check(Y,Z);
	tppi_1(Z,Y), eq_2(X,Z).
tppi_2(X,Y) :- tppi_2_(X,Y).

tpp_2_(X,Y) :- 
	tpp_1(X,Y);
	tpp_1(X,Z), eq_2_check(Y,Z);
	tpp_1(Z,Y), eq_2(X,Z).
tpp_2(X,Y) :- tpp_2_(X,Y).

tpp_2_check(X,Y) :- tpp_2(X,Y), !.


ntpp_2(X,Y)  :- 
	ntpp_2_(X,Y).

%%maybe in future change it to be like directional part (below)
ntpp_2_(X,Y) :-
	ntpp_2_(X,Y,[]);
	

	eq_2(X,Z),
	ntpp_2_check(Z,Y, [X]);


	ntpp_2_(X,Z,[]),
	eq_2_check(Z,Y).


ntpp_2_(X,Z,_) :- 
	ntpp_1(X,Z).

ntpp_2_(X,Z, Visited) :-

	tpp_1(Y,Z), 
	Y \= Z, 
	\+ member(Y, Visited),
	ntpp_2_(X,Y, [Y|Visited]),
	Y \= X,
	X \= Z;

	tpp_1(X,Y),
	Y \= X, 
	\+ member(Y, Visited),
	tpp_2(Y,Z),
	Y \= Z,
	X \= Z;

	ntpp_1(X,Y), 
	X \= Y, 
	\+ member(Y, Visited),
	ntpp_2_(Y,Z, [Y|Visited]),
	Y \= Z,
	X \= Z.


ntpp_2_check(X,Y,Forbiden_list) :- 
	
	ntpp_2_(X,Y,Forbiden_list).


ntppi_2(X,Y) :- ntpp_2(Y,X).


dc_3(X,Y) :- dc_3_(X,Y).

dc_3_(X,Y) :- 
	dc_2(X,Y);

	dc_3__(X,Y);

	dc_3__(Y,X).

dc_3__(X,Y) :-

	ntpp_2(X,Z), 
	dc_2_check(Z,Y); 

	tpp_2(X,Z), 
	dc_2_check(Z,Y); 


	ntpp_2(X,Z), 
	ntpp_2(Y,H), 
	dc_2_check(Z,H); 

	ntpp_2(X,Z), 
	tpp_2(Y,H), 
	dc_2_check(Z,H); 

	tpp_2(X,Z), 
	ntpp_2(Y,H), 
	dc_2_check(Z,H); 

	tpp_2(X,Z), 
	tpp_2(Y,H), 
	dc_2_check(Z,H). 


%transitivity
%combination_of_topological_and_directional

%eq_rel

left_3(X,Z) :-
	left_2_and_eq(X,Z);

	left_3__(X,Z).

left_2_and_eq(X,Z) :- 
	left_2(X,Z);

	eq_2(X,Y),
	left_2_check(Y,Z);

	eq_2(Y,Z),
	left_2_check(X,Y).

left_3__(X,Z) :- 
	

	has_pp_rel(X,Y),
	X \= Y,
	left_2_and_eq(Y,H),
	Y \= H,
	has_ppi_rel(H,Z),
	H \= Z;

	has_pp_rel(X,Y),
	X \= Y,
	left_2_and_eq(Y,Z),
	Y \= Z;

	left_2_and_eq(X,H),
	X \= H,
	has_ppi_rel(H,Z),
	H \= Z.

right_3(X,Z) :-
	left_3(Z,X).

above_3(X,Z) :-
	above_2_and_eq(X,Z);

	above_3__(X,Z).

above_2_and_eq(X,Z) :- 

	above_2(X,Z);

	eq_2(X,Y),
	above_2_check(Y,Z);

	eq_2(Y,Z),
	above_2_check(X,Y).

above_3__(X,Z) :- 

	has_pp_rel(X,Y),
	X \= Y,
	above_2_and_eq(Y,H),
	Y \= H,
	has_ppi_rel(H,Z),
	H \= Z;

	has_pp_rel(X,Y),
	X \= Y,
	above_2_and_eq(Y,Z),
	Y \= Z;

	above_2_and_eq(X,H),
	X \= H,
	has_ppi_rel(H,Z),
	H \= Z.


below_3(X,Z) :-
	above_3(Z,X).


behind_3(X,Z) :-
	behind_2_and_eq(X,Z);

	behind_3__(X,Z).

behind_2_and_eq(X,Z) :- 

	behind_2(X,Z);

	eq_2(X,Y),
	behind_2_check(Y,Z);

	eq_2(Y,Z),
	behind_2_check(X,Y).

behind_3__(X,Z) :- 

	has_pp_rel(X,Y),
	X \= Y,
	behind_2_and_eq(Y,H),
	Y \= H,
	has_ppi_rel(H,Z),
	H \= Z;

	has_pp_rel(X,Y),
	X \= Y,
	behind_2_and_eq(Y,Z),
	Y \= Z;

	behind_2_and_eq(X,H),
	X \= H,
	has_ppi_rel(H,Z),
	H \= Z.

front_3(X,Z) :-
	behind_3(Z,X).



%start
%combination_of_distantial_and_topological

far_2(X,Y) :-
	far_2_check(X,Y);
	far_2__(X,Y).

far_2_check(X,Y) :- 
	far_1(X,Y);

	far_1(X,H),
	eq_2_check(H,Y);

	far_1(H,Y),
	eq_2_check(X,H).

far_2__(X,Y) :-
	
	has_pp_rel(X,H),
	X \= H,
	far_2_check(H,Z),
	H \= Z,
	has_ppi_rel(Z,Y),
	Z \= Y;


	has_pp_rel(X,H),
	X \= H,
	far_2_check(H,Y),
	H \= Y;

	far_2_check(X,Z),
	X \= Z,
	has_ppi_rel(Z,Y),
	Z \= Y.


near_2(X,Y) :-
	near_2_check(X,Y).

near_2_check(X,Y) :- 
	near_1(X,Y);

	near_1(X,H),
	eq_2_check(H,Y);

	near_1(H,Y),
	eq_2_check(X,H);
	
	eq_2(X,Y).
	%ec_2(X,Y);
	%po_2(X,Y).


has_pp_rel(X,Y) :-

	ntpp_2(X,Y),
	X \= Y;
	
	tpp_2(X,Y),
	X \= Y.

has_ppi_rel(X,Y) :-
	
	ntppi_2(X,Y),
	X \= Y;
	
	tppi_2(X,Y),
	X \= Y.

%% existed_in relation description
%% only applied to spartqa dataset

existed_in_1(X,Y) :- 
	
	existed_in_(X,Y,[]);


	has_pp_rel(X,Z),
	existed_in_check(Z,Y,[X]);

	has_dir_or_dis(X,Z),
	existed_in_check(Z,Y,[X]).


existed_in_(X,Y,_) :- 
	
	has_pp_rel(X,Y).

existed_in_(X,Z, Visited) :-
	
	has_pp_rel(X,Y),
	Y \= Z, 
	\+ member(Y, Visited),
	existed_in_(Y,Z, [Y|Visited]),
	Y \= X,
	X \= Z;

	has_dir_or_dis(X,Y),
	Y \= Z, 
	\+ member(Y, Visited),
	existed_in_(Y,Z, [Y|Visited]),
	Y \= X,
	X \= Z.

existed_in_check(X,Y, Forbiden_list) :- 

	existed_in_(X,Y, Forbiden_list), !.

has_dir_or_dis(X,Y) :- 
	
	left_1(X,Y);
	right_1(X,Y);
	below_1(X,Y);
	above_1(X,Y);
	front_1(X,Y);
	behind_1(X,Y);

	near_1(X,Y);
	far_1(X,Y).


%%final conversion
%existed_in just for spartqa
existed_in(X,Y) :- existed_in_1(X,Y).
% existed_in_reverse(X,Y) :- existed_in_1(Y,X).

%directional
left(X,Y)   :-  left_3(X,Y).
right(X,Y)  :-  right_3(X,Y).
below(X,Y)  :-  below_3(X,Y).
above(X,Y)  :-  above_3(X,Y).
front(X,Y)  :-  front_3(X,Y).
behind(X,Y) :-  behind_3(X,Y).

%topological
ntppi(X,Y) :- ntppi_2(X,Y) .
%; existed_in_reverse(X,Y).
ntpp(X,Y)  :- ntpp_2(X,Y).
%; existed_in(X,Y).
tppi(X,Y)  :- tppi_2(X,Y).
tpp(X,Y)   :- tpp_2(X,Y).
ec(X,Y)    :- ec_2(X,Y).
po(X,Y)    :- po_2(X,Y).
dc(X,Y)    :- dc_3(X,Y).
eq(X,Y)    :- eq_2(X,Y).

%distantial
near(X,Y) :- near_2(X,Y).
far(X,Y)  :- far_2(X,Y).




%%Work on the size for the distantial relations 
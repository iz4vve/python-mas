:- dynamic bounce/1 turn_off/1, waited_tick/1


%
% Surge protection
%

% counts how many wait iterations
waited(Count) :-
    aggregate_all(count, waited_tick(X), Count).

% too_many_bounces(Host, X) :-
%     count_bounce_requests(Host, Count), Count>X.

% too_many_turn_offs(Host, X) :-
%     count_turn_off_requests(Host, Count), Count>X.

count_all_bounce_requests(Count) :-
    aggregate_all(count, bounce(_), Count).

count_bounce_requests(Host, Count) :-
    aggregate_all(count, bounce(Host), Count).

count_all_turn_off_requests(Count) :-
    aggregate_all(count, turn_off(_), Count).

count_turn_off_requests(Host, Count) :-
    aggregate_all(count, turn_off(Host), Count).

% counts of all requests
too_many_requests(Count, X) :-
    count_all_bounce_requests(Bounce),
    count_all_turn_off_requests(Turnoff),
    Bounce + Turnoff > X.

% in surge if too many requests or not waited long enough
in_surge(Actions, Timer) :-
    too_many_requests(Count, Actions)
    waited(Y), Y < Timer.
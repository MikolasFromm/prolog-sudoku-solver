% initialize to be called from outside
:- initialization(main, main).

% solving module
:- use_module(library(clpfd)).

% Load predicates from "input.pl"
:- include("sudoku_input.pl").

sudoku(Rows) :-
    size(Size),  %% save the size of the board
    board(Rows),  %% save the board
    SquareSize is Size * Size,
    %% size check
    length(Rows, SquareSize), %% enough rows check
    maplist(length_(SquareSize), Rows), %% enough items in each row

    % %% distinct check for rows and columns
    maplist(all_different, Rows), %% all item different in each row
    transpose(Rows, Columns),
    maplist(all_different, Columns), %% all item different in each column

    %% distinct check for squares
    squares(Rows, Size, Squares),
    maplist(all_different, Squares),
    
    maplist(xySquareRange(Size), Squares).

%% custom length_ for better maplist usage
length_(Size, Rows) :- length(Rows, Size).

%% gets only a section of a list
subslice(Length, 0, List, Sub) :-
    length(Sub, Length), 
    append(Sub, _, List), 
    !.

subslice(Length, StartIndex, [_|Rest], Sub) :-
    X is StartIndex - 1,
    subslice(Length, X, Rest, Sub).

%% get all multipies of a number
multiples(Num, Multiples) :-
    Max is Num * Num - 1,
    findall(X, (between(0, Max, X), 0 is X mod Num), Multiples).

xySquareRange(Size, Square) :-
    Max is Size * Size,
    maplist(between(1, Max), Square). %% all values between 1 and Max

%% get all values in a square
xySquare(Rows, Size, XIndex, YIndex, Square) :-
    subslice(Size, XIndex, Rows, SubRows), %% get the required rows
    maplist(subslice(Size, YIndex), SubRows, SubSquares), %% get the required columns
    foldl(append, SubSquares, [], Square). %% flatten the list

%% get all squares in a row
xSquares(Rows, Size, XIndex, Squares) :-
    multiples(Size, Indexy), %% create all indexes
    maplist(xySquare(Rows, Size, XIndex), Indexy, Squares). %% get all elements for each index

%% get all squares
squares(Rows, Size, SquaresList) :-
    multiples(Size, Indexy), %% create all indexes
    maplist(xSquares(Rows, Size), Indexy, Squares), %% get all squares for each index
    foldl(append, Squares, [], SquaresList). %% flatten the list

solve_sudoku() :-
    sudoku(Rows),
    maplist(writeln, Rows),
    export_rows_to_file("sudoku_output.txt", Rows), !.

%% EXPORTING
% Export a list of rows to a file
export_rows_to_file(Filename, Rows) :-
    open(Filename, write, Stream),
    export_rows(Stream, Rows),
    close(Stream).

% Recursively write rows to the file
export_rows(_, []).
export_rows(Stream, [Row | Rest]) :-
    write(Stream, Row), % Write the current row to the file
    nl(Stream),         % Add a newline after each row
    export_rows(Stream, Rest). % Recursively process the rest of the rows

main :-
    solve_sudoku(),
    halt.
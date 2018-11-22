#! /usr/bin/python3

from collections import Counter
from collections import defaultdict
import itertools
import sys


class ModifiedPCP:

    def __init__(self, a_strings, b_strings):
        self.a_strings = a_strings
        self.b_strings = b_strings
        self.s_options_total = list(range(len(self.a_strings)))
        self.final_sequence = ''

        self.solve()

    def tree(self):
        return defaultdict(self.tree)

    def make_tree(self, strings):
        """Make ordered tree data structure where each node is letter from string.

        This is implemented to speed up substring search.

        Args:
            strings (list of strings): Strings to build tree.

        Returns:
            tree (dict): Tree of strings.

        """
        # start from tree root
        root = self.tree()
        # mark if letter is the end of string or just its part
        root['end'] = set()
        root['part'] = set(self.s_options_total)
        for idx, string in enumerate(strings):
            node = root
            for letter in string:
                new_node = node[letter]
                new_node.setdefault('end', set())
                new_node.setdefault('part', set()).add(idx)
                node = new_node
            node['end'].add(idx)
            node['part'].remove(idx)

        return root

    def search_in_tree(self, tree, substring):
        """Search in tree for appropriate incomplete and complete matches for substring.

        Args:
            tree (dict): Tree of strings.
            substring (str): Substring to be matched.

        Returns:
            s_options_for_match (set): Set of s options for substring match.

        """
        s_options_for_match = set()
        node = tree
        idx = 0
        substring_length = len(substring)
        while idx < substring_length and len(node[substring[idx]]) != 0:
            node = node[substring[idx]]
            s_options_for_match.update(node['end'])
            idx += 1
        if idx == substring_length:
            s_options_for_match.update(node['part'])

        return s_options_for_match

    def prefix_filter(self):
        """Find all pairs where one string is the prefix of the other.

        Prefix filter helps to find all candidates for sequence beginning.
        Idea of prefix filter is introduced in paper of Richard J. Lorentz
        'Creating Difficult Instances of the Post Correspondence Problem'.

        Returns:
            s_options_for_beginning (set): Set of s options for sequence beginning.

        """
        s_options_for_beginning = set()
        for s in self.s_options_total:
            a_line = a_lines[s]
            b_line = b_lines[s]
            if a_line.startswith(b_line) or b_line.startswith(a_line):
                s_options_for_beginning.add(s)

        return s_options_for_beginning

    def postfix_filter(self):
        """Find all pairs where one string is the postfix of the other.

        Postfix filter helps to find all candidates for sequence ending.
        Idea of postfix filter is introduced in paper of Richard J. Lorentz
        'Creating Difficult Instances of the Post Correspondence Problem'.

        Returns:
            s_options_for_ending (set): Set of s options for sequence ending.

        """
        s_options_for_ending = set()
        for s in self.s_options_total:
            a_line = a_lines[s]
            b_line = b_lines[s]
            if a_line.endswith(b_line) or b_line.endswith(a_line):
                s_options_for_ending.add(s)

        return s_options_for_ending

    def length_balance_filter(self, s_options_for_beginning, s_options_for_ending):
        """Find all pairs combinations that are balanced by length.

        Length balance filter is applied on s combinations after prefix and postfix filter for saving time.
        Idea of length balance filter is introduced in paper of Richard J. Lorentz
        'Creating Difficult Instances of the Post Correspondence Problem'.

        Args:
            s_options_for_beginning (set): Set of s options for sequence beginning.
            s_options_for_ending (set): Set of s options for sequence ending.

        Returns:
            s_combinations_by_length (dict): Dictionary of format {length: list of combinations}.

        """
        s_combinations_by_length = {}
        a_strings_length = list(map(len, self.a_strings))
        b_strings_length = list(map(len, self.b_strings))
        for s_number in range(1, len(self.a_strings) + 1):
            for combination in itertools.combinations(self.s_options_total, s_number):
                a_length_sum = sum([a_strings_length[i] for i in combination])
                b_length_sum = sum([b_strings_length[i] for i in combination])
                if a_length_sum == b_length_sum:
                    if set(combination).intersection(s_options_for_beginning) and set(combination).intersection(s_options_for_ending):
                        s_combinations_by_length.setdefault(a_length_sum, []).append(combination)

        return s_combinations_by_length

    def elements_balance_filter(self, s_combinations_by_length):
        """Find all pairs combinations that are balanced by elements.

        Elements balance filter is applied on s combinations after length balance filter for saving time.
        Idea of elements balance filter is introduced in paper of Richard J. Lorentz
        'Creating Difficult Instances of the Post Correspondence Problem'.

        Args:
            s_combinations_by_length (dict): Dictionary of format {length: list of combinations}.

        Returns:
            s_combinations_by_elements (dict): Dictionary of format {length: list of combinations}.

        """
        s_combinations_by_elements = {}
        for length, combinations in s_combinations_by_length.items():
            for combination in combinations:
                a_unordered_sequence = ''.join([self.a_strings[s] for s in combination])
                b_unordered_sequence = ''.join([self.b_strings[s] for s in combination])
                if Counter(a_unordered_sequence) == Counter(b_unordered_sequence):
                    s_combinations_by_elements.setdefault(length, []).append(combination)

        return s_combinations_by_elements

    def dfs(self, s_taken=set(), a_sequence='', b_sequence='', a_index=0, b_index=0):
        """Try to find the lexicographically shortest sequence using depth-first search for combination of particular length.

        Args:
            s_taken (set): Set of already used s values.
            a_sequence (str): Current a sequence.
            b_sequence (str): Current b sequence.
            a_index (int): Last index of current a sequence.
            b_index (int): Last index of current b sequence.

        """
        if a_index < b_index:
            substring = b_sequence[a_index:]
            s_options = self.search_in_tree(self.a_tree, substring)
        elif a_index > b_index:
            substring = a_sequence[b_index:]
            s_options = self.search_in_tree(self.b_tree, substring)
        else:
            s_options = self.s_options_for_beginning

        start = min(a_index, b_index)
        for s in s_options:
            if s in self.combination and s not in s_taken:
                a_string = self.a_strings[s]
                b_string = self.b_strings[s]
                a_sequence_new = a_sequence + a_string
                b_sequence_new = b_sequence + b_string
                a_index_new = a_index + len(a_string)
                b_index_new = b_index + len(b_string)
                end = min(a_index_new, b_index_new)
                if a_sequence_new[start:end] == b_sequence_new[start:end]:

                    if a_index_new == b_index_new:
                        if not self.final_sequence:
                            self.final_sequence = a_sequence_new
                        else:
                            self.final_sequence = min(self.final_sequence, a_sequence_new)
                        continue

                    s_taken_new = s_taken.copy()
                    s_taken_new.add(s)
                    self.dfs(s_taken_new, a_sequence_new, b_sequence_new, a_index_new, b_index_new)

    def solve(self):
        """Find the shortest (by length and lexicographically) sequence for modified PCP (if it is possible to form one),
           or return 'IMPOSSIBLE' (if it is not possible to solve the problem).

            Algorithm is the following:
            - apply prefix filter
            - apply postfix filter
            - apply length balance filter (on the result after prefix and postfix filter)
            - apple elements balance filter (on the result after length balance filter)
            - sort filtered combinations by its elements length in ascending order
            - for each combinations length try to find the lexicographically shortest sequence using depth-first search
            - return sequence as soon as we got one,
              otherwise - return 'IMPOSSIBLE'

        """
        self.a_tree = self.make_tree(self.a_strings)
        self.b_tree = self.make_tree(self.b_strings)

        # apply prefix filter
        self.s_options_for_beginning = self.prefix_filter()
        if len(self.s_options_for_beginning) == 0:
            self.final_sequence = 'IMPOSSIBLE'
            return

        # apply postfix filter
        self.s_options_for_ending = self.postfix_filter()
        if len(self.s_options_for_ending) == 0:
            self.final_sequence = 'IMPOSSIBLE'
            return

        # apply length balance filter (on the result after prefix and postfix filter)
        self.s_combinations_by_length = self.length_balance_filter(self.s_options_for_beginning,
                                                                   self.s_options_for_ending)
        if len(self.s_combinations_by_length) == 0:
            self.final_sequence = 'IMPOSSIBLE'
            return

        # apple elements balance filter (on the result after length balance filter)
        self.s_combinations_by_elements = self.elements_balance_filter(self.s_combinations_by_length)
        if len(self.s_combinations_by_elements) == 0:
            self.final_sequence = 'IMPOSSIBLE'
            return

        # sort filtered combinations by its elements length in ascending order
        self.s_combinations_filtered = sorted(self.s_combinations_by_elements.items())

        # for each combinations length try to find the lexicographically shortest sequence using depth-first search
        for length, combinations in self.s_combinations_filtered:
            for combination in combinations:
                self.combination = combination
                self.dfs()

            # return sequence as soon as we got one
            if self.final_sequence:
                return

        # otherwise - return 'IMPOSSIBLE'
        if not self.final_sequence:
            self.final_sequence = 'IMPOSSIBLE'
            return


if __name__ == "__main__":
    #sys.stdin = open('sample-01.in', 'r')

    case_idx = 1
    while True:
        case_nb_lines = sys.stdin.readline()
        if not case_nb_lines:
            break

        a_lines = []
        b_lines = []
        for s in range(int(case_nb_lines)):
            a, b = sys.stdin.readline().split()
            a_lines.append(a)
            b_lines.append(b)

        modified_pcp = ModifiedPCP(a_lines, b_lines)
        print('Case ' + str(case_idx) + ': ' + modified_pcp.final_sequence)

        case_idx += 1

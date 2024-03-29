from huffman_tree import generate_code_from_queue
from analyser import analyse_text, SEPARATORS, str_rep, is_valid_dict, separator_split
from imports import dumps
from exception_handler import IncorrectBinaryValueException, BinaryStringExpectedException
from exception_handler import CompressorExpectedStringException
from exception_handler import MakeCompressedStringExpectedStringException, MakeCompressedStringExpectedDictException
from exception_handler import MakeCompressedStringDictStructureException, MakeCompressedStringCorruptedCodeException

# This function converts binary (in string form) to decimal (only positive)
# Return type -> int
def binary_to_decimal(bin: str) -> int:

    # If the value passed is not a string literal, raise proper error
    if not isinstance(bin, str):
        raise BinaryStringExpectedException(f"""
Function Call : binary_to_decimal({bin = })
Provided Value {bin = } is not a string literal.
""")

    # Go through the string and see if each character is 0 or 1, if not
    # Raise proper error
    for i in bin:
        if i not in ['1', '0']:
            raise IncorrectBinaryValueException(f"""
Function Call : binary_to_decimal({bin = })
Provided Value {bin = } is incorrect binary string.
""")
        
    # Take the characters from right to left
    # multiply it with 2 ^ (position of the character from right - 1) and store it in a list
    # sum all the elements of that list
    num_10 = sum([int(bin[-i])*2**(i-1) for i in range(1, len(bin) + 1)])
    # return the new number formed
    return num_10

# This function will create the binary string for a given text based on the huffman code given
# Return type -> str
def make_compressed_string(text: str, huffman_codes: dict[str: str]) -> str:
    
    # Getting the validity and getting the string representation of huffman_codes
    # for easy error messages
    huffman_codes_validity = is_valid_dict(huffman_codes, str, str)
    str_rep_huffman_code = str_rep(huffman_codes)

    # If text is not a string, raising proper error
    if not isinstance(text, str):
        raise MakeCompressedStringExpectedStringException(f"""
Function Call : make_compressed_string({text = }, huffman_codes = {str_rep_huffman_code})
Provided Value {text = } is not a string literal.
""")
    
    # If huffman_codes is not a valid dictionary raising proper error
    if not huffman_codes_validity[0]:
        if len(huffman_codes_validity) == 2:
            key, value = huffman_codes_validity[1]
            raise MakeCompressedStringDictStructureException(f"""
Function Call : make_compressed_string({text = }, huffman_codes = {str_rep_huffman_code})
The Pair {key = }, {value = } in huffman_codes does not match the requirements (key: str, value: str).
""")
        raise MakeCompressedStringExpectedDictException(f"""
Function Call : make_compressed_string({text = }, {huffman_codes = })
Provided Value {huffman_codes = } is not a dictionary.
""")
    
    del huffman_codes_validity
    
    # Separating 1s and 0s from other characters
    ones_and_zeros = separator_split(text, '01')
    # Converting the 1s and 0s using our code before converting anything else
    ones_and_zeros = [''.join([huffman_codes[i] 
                            if i in huffman_codes.keys() else i 
                            for i in word]) 
                    if '1' in word or '0' in word else word 
                    for word in ones_and_zeros]
    # concatenating the list to form a new text with all 1s and 0s converted
    text = ''.join(ones_and_zeros)
    del ones_and_zeros
    # Separating words and separators
    # (which include 1 and 0 now because we dont want to convert them more than once)
    words = separator_split(text, SEPARATORS+'01')
    word_list = [i for i in huffman_codes.keys() if len(i) > 1]
    # Converting all the words (that are in the dictionary) using the code and leaving the rest
    words = [huffman_codes[word] 
            if word in word_list else word 
            for word in words]
    # concatenating the list to form a new text with all the words in dictionary converted
    text = ''.join(words)
    del words
    # Repeating the same process for the separate characters but this time only using
    # 1s and 0s as separators as everything other the them are already converted
    characters = separator_split(text, '10')
    try:
        characters = [''.join([huffman_codes[i] for i in word]) 
                    if not ('1' in word or '0' in word) else word 
                    for word in characters]
    except KeyError:
        raise MakeCompressedStringCorruptedCodeException(f"""
Function Call : make_compressed_string({text = }, huffman_codes = {str_rep_huffman_code})
Code does not contain one or more characters present in the string.
Conclusion - Code is corrupted.
""")
    # concatenating the list to form our final binary text with everything converted
    text = ''.join(characters)
    del characters
    # Returning the compressed binary text
    return text

# This function will call the functions of this file and other necessary files
# To produce the final string that should be written to the output file
# Return type -> str
def create_string_to_write(text: str) -> str:
    
    # if text is not a string literal raise proper error
    if not isinstance(text, str):
        raise CompressorExpectedStringException(f"""
Function Call : create_string_to_write({text = })
Provided Value {text = } is not a string literal.
""")

    # Getting the priority queue from the text to be compressed
    queue = analyse_text(text)
    # Setting the type of the code, so we are able to call functions from the type class
    # with ease
    huffman_codes: dict
    # Getting our code
    huffman_codes = generate_code_from_queue(queue)
    # Getting the final binary string
    compressed_string = make_compressed_string(text, huffman_codes)
    # To encode it to the file while preserving space,
    # we have to convert 8 consecutive bits to a unicode-8 character
    # to do that we have to make sure the binary string is divisible by 8
    mod8 = len(compressed_string) % 8
    # if the mod 8 wasn't 0 we have to add leading 0s so we need to store that information
    # in the file itself, so we are able to remove the leading 0s later as well
    added_zeros = 0
    if mod8:
        added_zeros = 8 - mod8
    # adding the 0s if any
    compressed_string = '0'*added_zeros + compressed_string
    # getting 8 bit binaries from the text into a list
    binaries = [compressed_string[i:i+8] for i in range(0,len(compressed_string),8)]
    # converting the 8 bit binaries to decimal numbers (so python can convert it into ASCII)
    decimals = [binary_to_decimal(i) for i in binaries]
    # converting the decimals to 8 bit ASCII / unicode characters
    characters = [chr(i) for i in decimals]
    # writing the zeros added, the 8 bit unicode compressed characters and the code to the final string
    final_string = f'{added_zeros}' + ''.join(characters) + '\n' + dumps(huffman_codes)
    # Deleting heavy data members to free space
    del characters, binaries, huffman_codes, decimals, compressed_string, queue, added_zeros
    # returning the final formed string that is ready to write in the final file
    return final_string

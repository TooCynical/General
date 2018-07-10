class LZW:
    FINAL_TOKEN = '#'
    def __init__(self, msg, verbose=1):


        self.verbose = verbose

        self.message = msg.lower()
        self.out = ""

        self.next_code = 0
        self.width = 5
        
        self.__set_initial_dict()
        self.__set_binary_msg()
        self.__compress()


    def compressed(self):
        return self.out


    def uncompressed(self):
        return self.binary_msg


    def __set_binary_msg(self):
        self.binary_msg = ""
        for char in self.message:
            self.binary_msg += self.__binary(char)
        self.binary_msg += self.__binary(LZW.FINAL_TOKEN)


    def __set_initial_dict(self):
        self.dict = {}
        self.__add_to_dict(LZW.FINAL_TOKEN)
        for i in range(26):
            char = chr(i + ord('a'))
            self.__add_to_dict(char)

    def __binary(self, token):
        return "{0:b}".format(self.dict[token]).zfill(self.width)


    def __add_to_dict(self, token):
        if (self.verbose > 0):
            print "Adding \'" + token + "\' to dict with code " + str(self.next_code)
        self.dict[token] = self.next_code
        self.next_code += 1
        if(self.next_code > 2**self.width + 1):
            self.width += 1


    def __output(self, token):
        self.out += self.__binary(token)


    def __close(self):
        self.__output(LZW.FINAL_TOKEN)


    def __compress(self):
        buffer = ""
        next_buffer = ""
        for i in xrange(len(self.message)):
            next_buffer = buffer + self.message[i]
            if not next_buffer in self.dict:
                self.__add_to_dict(next_buffer)
                self.__output(buffer)
                buffer = self.message[i]
            else:
                buffer += self.message[i]
        self.__output(buffer)
        self.__close()


c = LZW("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", verbose = 0)
print len(c.compressed())
print len(c.uncompressed())
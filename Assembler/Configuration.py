#! /usr/bin/python3

# To concatenate range() iterators
from itertools  import chain
from math       import ceil

class DefaultOffset:
    """Calculates the run-time offsets applied by the CPU to accesses in private memory,
       so that all available private memory is equally distributed amongst the threads.
       Set the offsets in a memory init file so we don't have to do a tedious init
       code sequence. These offsets normally never change at runtime."""

    def __init__ (self, data_mem_depth, start_of_private_mem, thread_count):
        # Divide between threads the remaining data memory after the shared memory range.
        self.private_mem_depth  = ceil((data_mem_depth - start_of_private_mem) / thread_count)
        self.default_offset     = [(self.private_mem_depth * thread) for thread in range(thread_count)]

class MemoryMap:
    """Describes the static properties of the data address space: shared, private, and high,
       all zero-based, as the CPU applies default offsets to private mem accesses at runtime."""

    def __init__ (self, memory_shared_count, memory_indirect_base, memory_indirect_count, memory_io_base, memory_io_count, default_offset_obj):
        # Shared memory (all threads): 
        self.shared     = range(memory_shared_count)
        # Shared Literal Pool (Zero is reserved as zero-register, implemented by hardware also)
        self.pool       = range(1, memory_indirect_base)
        self.indirect   = range(memory_indirect_base, memory_indirect_base + memory_indirect_count)
        self.io         = range(memory_io_base, memory_io_base + memory_io_count)

        # Private memory range for one thread, no offset applied.
        self.private    = range(memory_shared_count, memory_shared_count + default_offset_obj.private_mem_depth)

        # Total thread mem is shared + private, mapped consecutively.
        self.total      = chain(self.shared, self.private)

        # Base write addresses.
        # Add these to A/B read address to get write address.
        # I is only readable by the Program Counter, writable by code.
        # H is only writable by code. Not readable at all.
        self.write_bases = {"A":0, "B":1024, "I":2048, "H":3072}

        # Config registers write addresses in write-only H (high) memory
        # ECL XXX FIXME These should be computed from configuration, not hardcoded.
        self.s              = 3072
        self.a_po           = [3076,3077,3078,3079]
        self.b_po           = [3080,3081,3082,3083]
        self.da_po          = [3084,3085,3086,3087]
        self.db_po          = [3088,3089,3090,3091]
        self.do             = 3092
        self.bs1_sentinel   = [3100,3106,3112,3118]
        self.bs1_mask       = [3101,3107,3113,3119]
        self.bs2_sentinel   = [3102,3108,3114,3120]
        self.bs2_mask       = [3103,3109,3115,3121]
        self.bc             = [3104,3110,3116,3122]
        self.bd             = [3105,3111,3117,3123]
        self.od             = [3200,3201,3202,3203,3204,3205,3206,3207,3208,3209,3210,3211,3212,3213,3214,3215]

    def read_to_write_address (self, read_address, memory):
        if memory == "A" or memory == "B":
            return read_address + self.write_bases[memory]
        print("Memory range {0} is not not readable, so no read address conversion is possible (absolute write address)".format(memory))
        exit(1)

class Configuration:
    """Place system configuration parameters here. Any hardcoded value goes here."""

    def __init__ (self):
        self.thread_count           = 8
        self.memory_depth_words     = 1024
        self.memory_width_bits      = 36
        self.memory_shared_count    = 32
        # Indirect and I/O memory must fit in shared, and match hardware
        self.memory_indirect_base   = 24
        self.memory_indirect_count  = 4
        self.memory_io_base         = 28
        self.memory_io_count        = 4
        self.default_offset         = DefaultOffset (self.memory_depth_words, self.memory_shared_count, self.thread_count)
        self.memory_map             = MemoryMap (self.memory_shared_count, self.memory_indirect_base, self.memory_indirect_count, self.memory_io_base, self.memory_io_count, self.default_offset)

